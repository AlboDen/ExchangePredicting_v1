import numpy as np
from numpy.polynomial import Polynomial
from pyparsing import countedArray
from scipy.integrate import quad

from network.DataBase import DataBaseManager
from scipy.stats import pearsonr
import numpy as np
from itertools import combinations
import numpy as np
from sklearn.linear_model import LinearRegression
from scipy.optimize import curve_fit
from itertools import combinations

class Statistic:

    class OrderBookRegressions:
        regression_area_asks = None
        regression_area_bids = None

        @staticmethod
        def __bestRegression(x, y, max_degree=5, folds=5, random_state=42):
            x = np.asarray(x, dtype=float).ravel()
            y = np.asarray(y, dtype=float).ravel()

            if len(x) != len(y):
                raise ValueError("Массивы x и y должны иметь одинаковую длину.")
            if len(x) < 3:
                raise ValueError("Нужно минимум 3 наблюдения.")
            if not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)):
                raise ValueError("Массивы не должны содержать NaN или бесконечности.")
            if np.ptp(x) == 0:
                raise ValueError("В массиве x должно быть хотя бы два различных значения.")
            if folds < 2:
                raise ValueError("folds должен быть не меньше 2.")

            folds = min(folds, len(x))
            max_test_size = int(np.ceil(len(x) / folds))
            min_train_size = len(x) - max_test_size
            allowed_max_degree = min(max_degree, min_train_size - 1)

            if allowed_max_degree < 1:
                raise ValueError("Недостаточно данных для построения регрессии.")

            candidates = [("linear", 1)]
            for degree in range(2, allowed_max_degree + 1):
                candidates.append(("polynomial", degree))

            if np.all(y > 0):
                candidates.append(("exponential", None))

            def fit_model(model_type, degree, x_train, y_train):
                if model_type == "exponential":
                    # Храним [log_a, b] для численной стабильности
                    b, log_a = np.polyfit(x_train, np.log(y_train), 1)
                    return np.array([log_a, b])

                poly = Polynomial.fit(x_train, y_train, degree).convert()
                return poly.coef[::-1]

            def predict(model_type, coefficients, x_values):
                if model_type == "exponential":
                    log_a, b = coefficients
                    with np.errstate(over="ignore", invalid="ignore"):
                        return np.exp(log_a + b * x_values)
                return np.polyval(coefficients, x_values)

            def area_under_model(model_type, coefficients, x_min, x_max):
                if model_type == "linear":
                    k, b = coefficients
                    return k * (x_max ** 2 - x_min ** 2) / 2 + b * (x_max - x_min)

                if model_type == "polynomial":
                    integral_coeffs = np.polyint(coefficients)
                    F = lambda x: np.polyval(integral_coeffs, x)
                    return F(x_max) - F(x_min)

                log_a, b = coefficients
                if b == 0:
                    return np.exp(log_a) * (x_max - x_min)

                def func(x_val):
                    with np.errstate(over="ignore", invalid="ignore"):
                        return np.exp(log_a + b * x_val)

                result, error = quad(func, x_min, x_max, epsabs=1e-9, epsrel=1e-9)
                return result

            rng = np.random.default_rng(random_state)
            indices = rng.permutation(len(x))
            validation_folds = np.array_split(indices, folds)

            scores = {}

            for model_type, degree in candidates:
                squared_errors = []
                valid = True

                for validation_idx in validation_folds:
                    train_mask = np.ones(len(x), dtype=bool)
                    train_mask[validation_idx] = False

                    try:
                        coeffs = fit_model(
                            model_type,
                            degree,
                            x[train_mask],
                            y[train_mask]
                        )

                        prediction = predict(model_type, coeffs, x[validation_idx])

                        if not np.all(np.isfinite(prediction)):
                            valid = False
                            break

                        squared_errors.extend((y[validation_idx] - prediction) ** 2)

                    except (ValueError, FloatingPointError, np.linalg.LinAlgError):
                        valid = False
                        break

                if valid and squared_errors:
                    name = (
                        "linear"
                        if model_type == "linear"
                        else "exponential"
                        if model_type == "exponential"
                        else f"polynomial_{degree}"
                    )
                    scores[name] = float(np.sqrt(np.mean(squared_errors)))

            if not scores:
                raise RuntimeError("Не удалось обучить ни одну модель.")

            best_name = min(scores, key=scores.get)

            if best_name == "linear":
                best_type, best_degree = "linear", 1
            elif best_name == "exponential":
                best_type, best_degree = "exponential", None
            else:
                best_type = "polynomial"
                best_degree = int(best_name.split("_")[1])

            best_coefficients = fit_model(best_type, best_degree, x, y)

            # Предсказания на всех исходных данных для подсчёта точек выше линии
            y_pred_all = predict(best_type, best_coefficients, x)
            points_above = int(np.sum(y > y_pred_all))

            if best_type == "linear":
                formula = "y = k*x + b"
            elif best_type == "exponential":
                formula = "y = a * exp(b*x)"
            else:
                formula = f"y = c{best_degree}*x^{best_degree} + ... + c1*x + c0"

            area = area_under_model(best_type, best_coefficients, np.min(x), np.max(x))

            # Конвертируем коэффициенты в «человеческий» вид только для экспоненты в return
            final_coefficients = best_coefficients.tolist()
            if best_type == "exponential":
                log_a, b = best_coefficients
                a = np.exp(log_a)
                final_coefficients = [float(a), float(b)]

            return {
                "model": best_type,
                "degree": best_degree,
                "coefficients": final_coefficients,
                "formula": formula,
                "area_under_curve": float(area),
                "points_above_regression": points_above,
            }

        '''
        data to check correct:
            x = [0.0,1.0,2.0,3.0,4.0,5,6,7,8,9,10,11,12,13,14,15]
            y_exp = [1.0, 2.718281828, 7.389056099, 20.08553692, 54.59815003, 148,4131591, 403.4287935, 1096.633158, 2980.957987, 8103.083928, 22026.46579, 59874.14172, 162754.7914, 442413.392, 1202604.284]
            y_lin = [1,6, 11,16,21,26,31,36,41,46,51,56,61,66,71,76]
            y_3degree = [1, 9.2, 24.6, 48.4, 81.8, 126, 182.2, 251.6, 335.4, 434.8, 551, 685.2, 838.6, 1012.4, 1207.8, 1426]
        '''
        @staticmethod
        def calculateRegressionNumbers(x, y):
            bestRegress = Statistic.OrderBookRegressions.__bestRegression(x, y)
            buf = []
            match bestRegress['model']:
                case "linear":
                    counter = 2
                    for i in x:
                        # if counter != 0:
                        coefs = bestRegress['coefficients']
                        buf.append(coefs[0] * i + coefs[1])
                        # counter -= 1
                        # else:
                        #     counter = 2
                case "polynomial":
                    match bestRegress['degree']:
                        case 5:
                            for i in x:
                                coefs = bestRegress['coefficients']
                                buf.append(
                                    coefs[0] * i ** 5 + coefs[1] * i ** 4 + coefs[2] * i ** 3 + coefs[3] * i ** 1 + coefs[4] * i ** 1 + coefs[5])
                        case 4:
                            for i in x:
                                coefs = bestRegress['coefficients']
                                buf.append(coefs[0] * i ** 4 + coefs[1] * i ** 3 + coefs[2] * i ** 1 + coefs[3] * i ** 1 + coefs[4])
                        case 3:
                            for i in x:
                                coefs = bestRegress['coefficients']
                                buf.append(coefs[0] * i ** 3 + coefs[1] * i ** 2 + coefs[2] * i ** 1 + coefs[3])
                        case 2:
                            for i in x:
                                coefs = bestRegress['coefficients']
                                buf.append(coefs[0] * i ** 2 + coefs[1] * i ** 1 + coefs[2])

                case "exponential": #a*exp(b*x)
                    for i in x:
                        coefs = bestRegress['coefficients']
                        #print("TOOO LAAAAARGE",coefs[0] * 2.71**(coefs[1]*i), "bestRegress",bestRegress)
                        try:
                            buf.append(coefs[0] * 2.71**(coefs[1]*i))
                        except OverflowError:
                            print("OVERFLOWWWWWWWWWWW",coefs[0] * 2.71**(coefs[1]*i))
                            buf.append(coefs[0] * 2.71 ** (coefs[1] * i))
            return bestRegress['model'], x, buf, bestRegress['area_under_curve'], bestRegress['points_above_regression']


        @staticmethod
        def calcSlopeLinearReg(x, y):
            """
            Рассчитывает коэффициент наклона (k) линейной регрессии y = k*x + b.

            Parameters
            ----------
            x, y : array-like
                Массивы одинаковой длины.

            Returns
            -------
            float
                Коэффициент наклона k.
            """
            x = np.asarray(x, dtype=float).ravel()
            y = np.asarray(y, dtype=float).ravel()

            if len(x) != len(y):
                raise ValueError("Массивы x и y должны иметь одинаковую длину.")
            if len(x) < 2:
                raise ValueError("Нужно минимум 2 наблюдения.")
            if not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)):
                raise ValueError("Массивы не должны содержать NaN или бесконечности.")
            if np.ptp(x) == 0:
                raise ValueError("В массиве x должно быть хотя бы два различных значения.")

            k, b = np.polyfit(x, y, 1)
            return float(k)

    class OrderBookStaticAnalisys:
        #STATIC
        areaUnderLine_bids = 1
        areaUnderLine_asks = 1

        squareArea_bids = None
        squareArea_asks = None

        points_above_regression_bids = 1
        points_above_regression_asks = 1

        #DYNAMIC
        TIME_INTERVAL_SEC = 30      # всего три замера: через TIME_INTERVAL_SEC секунд, через 2*TIME_INTERVAL_SEC секунд, через 3*TIME_INTERVAL_SEC секунд

        @staticmethod
        def __countPointsInThirds(x, y):
            """
            Вычисляет прямоугольник, охватывающий все точки, делит его на три
            равные части вдоль оси x и возвращает количество точек в каждой части.

            Parameters
            ----------
            x, y : array-like
                Массивы координат точек одинаковой длины.

            Returns
            -------
            dict
                {
                    "first_third":  int,  # точки в левой трети
                    "second_third": int,  # точки в средней трети
                    "third_third":  int,  # точки в правой трети
                    "bounds": {
                        "x_min": float, "x_max": float,
                        "y_min": float, "y_max": float,
                    },
                    "split_x": [float, float]  # границы деления по x
                }
            """
            x = np.asarray(x, dtype=float).ravel()
            y = np.asarray(y, dtype=float).ravel()

            if len(x) != len(y):
                raise ValueError("Массивы x и y должны иметь одинаковую длину.")
            if len(x) == 0:
                raise ValueError("Массивы не должны быть пустыми.")

            # Прямоугольник, охватывающий все точки
            x_min, x_max = float(np.min(x)), float(np.max(x))
            y_min, y_max = float(np.min(y)), float(np.max(y))

            # Границы деления на три равные части по x
            x_third1 = x_min + (x_max - x_min) / 3.0
            x_third2 = x_min + 2.0 * (x_max - x_min) / 3.0

            # Подсчёт точек в каждой трети
            first = int(np.sum(x < x_third1))
            second = int(np.sum((x >= x_third1) & (x < x_third2)))
            third = int(np.sum(x >= x_third2))

            # return first,second,third
            return{
                "first_third": first,
                "second_third": second,
                "third_third": third,
                "bounds": {
                    "x_min": x_min,
                    "x_max": x_max,
                    "y_min": y_min,
                    "y_max": y_max,
                },
                "split_x": [x_third1, x_third2],
            }

        @staticmethod
        def calculateParams(bidsPrice,bidsSize, asksPrice, asksSize):
            #STATIC
            Statistic.OrderBookStaticAnalisys.squareArea_bids = ((np.max(bidsPrice) - np.min(bidsPrice)) *
                                                                 (np.max(bidsSize) - np.min(bidsSize)))
            Statistic.OrderBookStaticAnalisys.squareArea_asks = ((np.max(asksPrice) - np.min(asksPrice)) *
                                                                 (np.max(asksSize) - np.min(asksSize)))
            asks_thirds = Statistic.OrderBookStaticAnalisys.__countPointsInThirds(asksPrice, asksSize)
            bids_thirds = Statistic.OrderBookStaticAnalisys.__countPointsInThirds(bidsPrice, bidsSize)

            #DYNAMIC
            # short_term_archive = DataBaseManager.DataBaseManager.itSelf.get_request_by_seconds_ago(1 * Statistic.StaticAnalisys.TIME_INTERVAL_SEC)
            # print("short_term_archive",short_term_archive)
            # medium_term_archive = DataBaseManager.DataBaseManager.itSelf.get_request_by_seconds_ago(5 * Statistic.StaticAnalisys.TIME_INTERVAL_SEC)
            # long_term_archive = DataBaseManager.DataBaseManager.itSelf.get_request_by_seconds_ago(10 * Statistic.StaticAnalisys.TIME_INTERVAL_SEC)
            short_term_archive = DataBaseManager.DataBaseManager.itSelf.get_request_by_seconds_ago(1 * Statistic.OrderBookStaticAnalisys.TIME_INTERVAL_SEC)
            # print("short_term_archive", short_term_archive)
            medium_term_archive = DataBaseManager.DataBaseManager.itSelf.get_request_by_seconds_ago(
                5 * Statistic.OrderBookStaticAnalisys.TIME_INTERVAL_SEC)
            long_term_archive = DataBaseManager.DataBaseManager.itSelf.get_request_by_seconds_ago(
                10 * Statistic.OrderBookStaticAnalisys.TIME_INTERVAL_SEC)
            try:
                return {
                "spread" : float(np.min(asksPrice) - np.max(bidsPrice)),
                "regression_area_ratio" : float(Statistic.OrderBookStaticAnalisys.areaUnderLine_asks /
                                                Statistic.OrderBookStaticAnalisys.areaUnderLine_bids),
                "rectangle_area_ratio" : float(Statistic.OrderBookStaticAnalisys.squareArea_asks /
                                               Statistic.OrderBookStaticAnalisys.squareArea_bids),
                "regression_coeff_ratio" : abs(float(Statistic.OrderBookRegressions.calcSlopeLinearReg(asksPrice, asksSize) /
                                                     Statistic.OrderBookRegressions.calcSlopeLinearReg(bidsPrice, bidsSize))),
                "points_above_regression_ratio"  : float(Statistic.OrderBookStaticAnalisys.points_above_regression_asks /
                                                         Statistic.OrderBookStaticAnalisys.points_above_regression_bids),
                "asks_third1_count" : asks_thirds["first_third"],
                "asks_third2_count" : asks_thirds["second_third"],
                "asks_third3_count" : asks_thirds["third_third"],
                "bids_third1_count" : bids_thirds["first_third"],
                "bids_third2_count" : bids_thirds["second_third"],
                "bids_third3_count" : bids_thirds["third_third"],

                "short_term_params" : {
                    "spread":                   float(np.min(asksPrice) - np.max(bidsPrice))
                                                    /float(short_term_archive["static_params"]["spread"]),
                    "regression_area_ratio":    float(Statistic.OrderBookStaticAnalisys.areaUnderLine_asks /
                                                      Statistic.OrderBookStaticAnalisys.areaUnderLine_bids)
                                                    /float(short_term_archive["static_params"]["regression_area_ratio"]),
                    "rectangle_area_ratio":     float(Statistic.OrderBookStaticAnalisys.squareArea_asks /
                                                      Statistic.OrderBookStaticAnalisys.squareArea_bids)
                                                    /float(short_term_archive["static_params"]["rectangle_area_ratio"]),
                    "regression_coeff_ratio":   abs(float(Statistic.OrderBookRegressions.calcSlopeLinearReg(asksPrice, asksSize) /
                                                          Statistic.OrderBookRegressions.calcSlopeLinearReg(bidsPrice, bidsSize)))
                                                    /float(short_term_archive["static_params"]["regression_coeff_ratio"]),
                    "points_above_regression_ratio": float(Statistic.OrderBookStaticAnalisys.points_above_regression_asks /
                                                           Statistic.OrderBookStaticAnalisys.points_above_regression_bids)
                                                    /float(short_term_archive["static_params"]["points_above_regression_ratio"]),
                    "asks_third1_count": asks_thirds["first_third"]
                                                    / float(short_term_archive["static_params"]["asks_third1_count"]),
                    "asks_third2_count": asks_thirds["second_third"]
                                                    / float(short_term_archive["static_params"]["asks_third2_count"]),
                    "asks_third3_count": asks_thirds["third_third"]
                                                    / float(short_term_archive["static_params"]["asks_third3_count"]),
                    "bids_third1_count": bids_thirds["first_third"]
                                                    / float(short_term_archive["static_params"]["bids_third1_count"]),
                    "bids_third2_count": bids_thirds["second_third"]
                                                    / float(short_term_archive["static_params"]["bids_third2_count"]),
                    "bids_third3_count": bids_thirds["third_third"]
                                                    / float(short_term_archive["static_params"]["bids_third3_count"]),

                    "equilibrium_vector_magnitude_growth_ratio" : 1,
                    "equilibrium_price_growth_ratio" : 1,
                    "equilibrium_demand_growth_ratio" : 1,
                    "open_price_growth_ratio" : 1,
                    "close_price_growth_ratio" : 1,
                    "max_price_growth_ratio" : 1,
                    "min_price_growth_ratio" : 1
                },


                "medium_term_params": {#
                    "spread": float(np.min(asksPrice) - np.max(bidsPrice))
                              / float(medium_term_archive["static_params"]["spread"]),
                    "regression_area_ratio": float(Statistic.OrderBookStaticAnalisys.areaUnderLine_asks /
                                                   Statistic.OrderBookStaticAnalisys.areaUnderLine_bids)
                                             / float(medium_term_archive["static_params"]["regression_area_ratio"]),
                    "rectangle_area_ratio": float(Statistic.OrderBookStaticAnalisys.squareArea_asks /
                                                  Statistic.OrderBookStaticAnalisys.squareArea_bids)
                                            / float(medium_term_archive["static_params"]["rectangle_area_ratio"]),
                    "regression_coeff_ratio": abs(
                        float(Statistic.OrderBookRegressions.calcSlopeLinearReg(asksPrice, asksSize) /
                              Statistic.OrderBookRegressions.calcSlopeLinearReg(bidsPrice, bidsSize)))
                                              / float(
                        medium_term_archive["static_params"]["regression_coeff_ratio"]),
                    "points_above_regression_ratio": float(Statistic.OrderBookStaticAnalisys.points_above_regression_asks /
                                                           Statistic.OrderBookStaticAnalisys.points_above_regression_bids)
                                                     / float(
                        medium_term_archive["static_params"]["points_above_regression_ratio"]),
                    "asks_third1_count": asks_thirds["first_third"]
                                         / float(medium_term_archive["static_params"]["asks_third1_count"]),
                    "asks_third2_count": asks_thirds["second_third"]
                                         / float(medium_term_archive["static_params"]["asks_third2_count"]),
                    "asks_third3_count": asks_thirds["third_third"]
                                         / float(medium_term_archive["static_params"]["asks_third3_count"]),
                    "bids_third1_count": bids_thirds["first_third"]
                                         / float(medium_term_archive["static_params"]["bids_third1_count"]),
                    "bids_third2_count": bids_thirds["second_third"]
                                         / float(medium_term_archive["static_params"]["bids_third2_count"]),
                    "bids_third3_count": bids_thirds["third_third"]
                                         / float(medium_term_archive["static_params"]["bids_third3_count"]),

                    "equilibrium_vector_magnitude_growth_ratio": 1,
                    "equilibrium_price_growth_ratio": 1,
                    "equilibrium_demand_growth_ratio": 1,
                    "open_price_growth_ratio": 1,
                    "close_price_growth_ratio": 1,
                    "max_price_growth_ratio": 1,
                    "min_price_growth_ratio": 1
                },
                "long_term_params": {
                    "spread": float(np.min(asksPrice) - np.max(bidsPrice))
                              / float(long_term_archive["static_params"]["spread"]),
                    "regression_area_ratio": float(Statistic.OrderBookStaticAnalisys.areaUnderLine_asks /
                                                   Statistic.OrderBookStaticAnalisys.areaUnderLine_bids)
                                             / float(long_term_archive["static_params"]["regression_area_ratio"]),
                    "rectangle_area_ratio": float(Statistic.OrderBookStaticAnalisys.squareArea_asks /
                                                  Statistic.OrderBookStaticAnalisys.squareArea_bids)
                                            / float(long_term_archive["static_params"]["rectangle_area_ratio"]),
                    "regression_coeff_ratio": abs(
                        float(Statistic.OrderBookRegressions.calcSlopeLinearReg(asksPrice, asksSize) /
                              Statistic.OrderBookRegressions.calcSlopeLinearReg(bidsPrice, bidsSize)))
                                              / float(
                        long_term_archive["static_params"]["regression_coeff_ratio"]),
                    "points_above_regression_ratio": float(Statistic.OrderBookStaticAnalisys.points_above_regression_asks /
                                                           Statistic.OrderBookStaticAnalisys.points_above_regression_bids)
                                                     / float(
                        long_term_archive["static_params"]["points_above_regression_ratio"]),
                    "asks_third1_count": asks_thirds["first_third"]
                                         / float(long_term_archive["static_params"]["asks_third1_count"]),
                    "asks_third2_count": asks_thirds["second_third"]
                                         / float(long_term_archive["static_params"]["asks_third2_count"]),
                    "asks_third3_count": asks_thirds["third_third"]
                                         / float(long_term_archive["static_params"]["asks_third3_count"]),
                    "bids_third1_count": bids_thirds["first_third"]
                                         / float(long_term_archive["static_params"]["bids_third1_count"]),
                    "bids_third2_count": bids_thirds["second_third"]
                                         / float(long_term_archive["static_params"]["bids_third2_count"]),
                    "bids_third3_count": bids_thirds["third_third"]
                                         / float(long_term_archive["static_params"]["bids_third3_count"]),

                    "equilibrium_vector_magnitude_growth_ratio": 1,
                    "equilibrium_price_growth_ratio": 1,
                    "equilibrium_demand_growth_ratio": 1,
                    "open_price_growth_ratio": 1,
                    "close_price_growth_ratio": 1,
                    "max_price_growth_ratio": 1,
                    "min_price_growth_ratio": 1
                }
                #
                #     # динамические параметры по срокам (если нужны)
                # short_term_params = {
                #     "spread": 0.65,
                #     "regression_area_ratio": 1.12,
                #     "equilibrium_price_growth_ratio": 0.03,
                #     "open_price_growth_ratio": 0.02,
                # },
                # medium_term_params = {
                #     "spread": 0.72,
                #     "regression_area_ratio": 1.18,
                #     "equilibrium_price_growth_ratio": 0.05,
                #     "close_price_growth_ratio": 0.04,
                # },
                # long_term_params = None
            }
            except (TypeError):
                # print("TypeError           -TypeError           -TypeError           -TypeError           -TypeError           -             TypeError           -")
                return {
                    "spread": 1,
                    "regression_area_ratio": 1,
                    "rectangle_area_ratio": 1,
                    "regression_coeff_ratio": 1,
                    "points_above_regression_ratio": 1,
                    "asks_third1_count": 1,
                    "asks_third2_count": 1,
                    "asks_third3_count": 1,
                    "bids_third1_count": 1,
                    "bids_third2_count": 1,
                    "bids_third3_count": 1,

                    "short_term_params": {
                        "spread": 1,
                        "regression_area_ratio": 1,
                        "rectangle_area_ratio": 1,
                        "regression_coeff_ratio": 1,
                        "points_above_regression_ratio": 1,
                        "asks_third1_count": 1,
                        "asks_third2_count": 1,
                        "asks_third3_count": 1,
                        "bids_third1_count": 1,
                        "bids_third2_count": 1,
                        "bids_third3_count": 1,

                        "equilibrium_vector_magnitude_growth_ratio": 1,
                        "equilibrium_price_growth_ratio": 1,
                        "equilibrium_demand_growth_ratio": 1,
                        "open_price_growth_ratio": 1,
                        "close_price_growth_ratio": 1,
                        "max_price_growth_ratio": 1,
                        "min_price_growth_ratio": 1
                    },


                    "medium_term_params": {
                        "spread": 1,
                        "regression_area_ratio": 1,
                        "rectangle_area_ratio": 1,
                        "regression_coeff_ratio": 1,
                        "points_above_regression_ratio": 1,
                        "asks_third1_count": 1,
                        "asks_third2_count": 1,
                        "asks_third3_count": 1,
                        "bids_third1_count": 1,
                        "bids_third2_count": 1,
                        "bids_third3_count": 1,

                        "equilibrium_vector_magnitude_growth_ratio": 1,
                        "equilibrium_price_growth_ratio": 1,
                        "equilibrium_demand_growth_ratio": 1,
                        "open_price_growth_ratio": 1,
                        "close_price_growth_ratio": 1,
                        "max_price_growth_ratio": 1,
                        "min_price_growth_ratio": 1
                    },
                    "long_term_params": {
                        "spread": 1,
                        "regression_area_ratio": 1,
                        "rectangle_area_ratio": 1,
                        "regression_coeff_ratio": 1,
                        "points_above_regression_ratio": 1,
                        "asks_third1_count": 1,
                        "asks_third2_count": 1,
                        "asks_third3_count": 1,
                        "bids_third1_count": 1,
                        "bids_third2_count": 1,
                        "bids_third3_count": 1,

                        "equilibrium_vector_magnitude_growth_ratio": 1,
                        "equilibrium_price_growth_ratio": 1,
                        "equilibrium_demand_growth_ratio": 1,
                        "open_price_growth_ratio": 1,
                        "close_price_growth_ratio": 1,
                        "max_price_growth_ratio": 1,
                        "min_price_growth_ratio": 1
                    }
                }

    class TimeSeriesAnalisys:
        class StandartMethods:
            class AutocorrelationResearch:
                @staticmethod
                def __getLagsWithBestCorr(timeSeries):
                    SAMPLE_VOLUME = 7
                    #xrp 7,
                    MIN_NUMB_OF_SAMPLES = 1     #xrp 1,

                    RELEVANT_CORR = 0.95         #btc 0.95,
                    RELEVANT_P_VALUE = 0.01     #xrp 0.01,

                    relevantLags = []
                    # print("start", len(timeSeries) - SAMPLE_VOLUME - MIN_NUMB_OF_SAMPLES)
                    # try:
                    maximymLag = len(timeSeries) - SAMPLE_VOLUME - MIN_NUMB_OF_SAMPLES
                    if maximymLag > 10:
                        maximymLag=10
                    for lag in range(maximymLag):
                        buf = []
                        # print("LAG #", lag)
                        for iter in range(len(timeSeries) - MIN_NUMB_OF_SAMPLES - SAMPLE_VOLUME):
                            a = timeSeries[iter:iter + SAMPLE_VOLUME]
                            b = timeSeries[iter + lag:iter + SAMPLE_VOLUME + lag]
                            if len(b) - len(a) != 0:
                                break
                            # print("\t\ta = ", a)
                            # print("\t\tb = ", b)
                            r, p_value = pearsonr(a, b)
                            # print("\t\tcorr = ", r, "  p-value = ", p_value)
                            buf.append([r, p_value])
                        buf = np.array(buf)
                        if np.all(buf[:, 1] < RELEVANT_P_VALUE) and np.all(abs(buf[:, 0]) > RELEVANT_CORR):
                            # print("ADDEDLAG #", lag)
                            relevantLags.append(lag)
                    return relevantLags



                    # return bestLag

                @staticmethod
                def getRelevantArrays(timeSeries):
                    relevantArrays = []
                    bestLags = Statistic.TimeSeriesAnalisys.StandartMethods.AutocorrelationResearch.__getLagsWithBestCorr(timeSeries)
                    # print("LAGS ", bestLags)
                    for i in bestLags:
                        relevantArrays.append(
                            timeSeries[i:]
                        )
                    # print("relevantArrays",relevantArrays)
                    return relevantArrays

        class Indicators:

            @staticmethod
            def check_changesIndicator(series: np.ndarray, depth: int = 1) -> float:
                """
                Суммирует изменения временного ряда за последние `depth` единиц времени, начиная с конца.

                Логика:
                  - Берется срез последних `depth+1` значений (чтобы получить `depth` изменений).
                  - Считаются разности: diff[i] = series[i+1] - series[i].
                  - Суммируются все разности.
                  - Если количество позитивных изменений >= количеству негативных, возвращается 0.
                  - Иначе возвращается сумма всех изменений.

                Параметры
                ---------
                series : np.ndarray (1D)
                    Одномерный массив значений временного ряда.
                depth : int
                    Количество шагов (изменений) для анализа, начиная с конца. Должно быть >= 1.

                Возвращает
                -----------
                float
                    Сумма изменений, либо 0 по условию.
                """
                if not isinstance(series, np.ndarray) or series.ndim != 1:
                    raise ValueError("series должен быть одномерным np.array")
                if depth < 1:
                    raise ValueError("depth должен быть >= 1")
                if len(series) < 2:
                    return 0.0

                # Берем последние `depth+1` значений
                window = series[-depth - 1:]
                diffs = np.diff(window)  # массив из depth элементов

                pos_count = np.sum(diffs > 0)
                neg_count = np.sum(diffs < 0)

                # if pos_count >= neg_count:
                #     return 0.0

                # if float(np.sum(diffs)) > 1:
                #     return True
                # else:
                #     return False
                return float(np.sum(diffs))

            # # Пример использования
            # series = np.array([10, 11, 12, 13, 14, 15, 14, 13, 12])
            # print(sum_last_changes_from_end(series, depth=4))  # -1.0 (последние 5 значений: 15 → 14 → 13 → 12 → 12)

        # @staticmethod
        # def _pearsonCorelation(x1, x2):
        #     r, p_value = pearsonr(x1, x2)
        #     print(f"r = {r:.4f}, p-value = {p_value:.4f}")
        #     return r, p_value

        @staticmethod
        def print_correlation_matrix_with_y(y_values, features_dict, y_name="y"):
            """
            Считает и печатает полную корреляционную матрицу, включая целевую переменную y.

            Параметры:
                y_values: список/массив значений целевой переменной
                features_dict: DataCombinations.params (словарь {name: [values]})
                y_name: имя, под которым y появится в матрице (по умолчанию "y")
            """
            # 1. Приводим y к numpy и проверяем длину
            y = np.asarray(y_values, dtype=float)
            n_total = len(y)

            if n_total == 0:
                print("Нет данных для y.")
                return

            # 2. Собираем все ряды в один словарь, добавляя y как отдельный признак
            all_series = {y_name: y}
            for name, values in features_dict.items():
                arr = np.asarray(values, dtype=float)
                if len(arr) == n_total:
                    all_series[name] = arr
                # Если длины не совпадают — пропускаем этот признак (редкий случай)

            names = list(all_series.keys())
            if len(names) < 2:
                print("Недостаточно рядов для построения матрицы (нужно минимум 2).")
                return

            # 3. Синхронизация по пропускам (pairwise clean)
            # Находим индексы, где ВСЕ ряды имеют валидные числа (не NaN)
            mask = np.ones(n_total, dtype=bool)
            for name in names:
                mask &= ~np.isnan(all_series[name])

            valid_indices = np.where(mask)[0]

            if len(valid_indices) < 2:
                print(f"После удаления пропусков осталось только {len(valid_indices)} наблюдений. Нужно минимум 2.")
                return

            # Формируем очищенные данные
            data_clean = np.column_stack([
                all_series[name][valid_indices] for name in names
            ])

            # 4. Считаем корреляционную матрицу
            corr_matrix = np.corrcoef(data_clean, rowvar=False)  # rowvar=False — каждый столбец это признак

            # Защита от скаляра (если вдруг остался 1 ряд после фильтрации)
            if np.isscalar(corr_matrix):
                corr_matrix = np.array([[corr_matrix]])

            # 5. Печатаем матрицу
            # Подбираем ширину под самое длинное имя
            max_name_len = max(len(name) for name in names)
            col_width = max(max_name_len, 12)  # минимум 12 символов


            # Строки
            for i, name in enumerate(names):
                row_str = f"{name:<{col_width}}  " + "".join(
                    f"{corr_matrix[i, 0]:>{col_width}.4f}"
                )
                if abs(corr_matrix[i, 0]) >= 0.16:
                    print(row_str)

        @staticmethod
        def _build_equation(intercept, var_names, coefs):
            """Собирает текстовое уравнение."""
            parts = [f"{intercept:.3f}"]
            for name, coef in zip(var_names, coefs):
                sign = "+" if coef >= 0 else "-"
                parts.append(f"{sign} {abs(coef):.3f}*{name}")
            return "y = " + " ".join(parts)

        @staticmethod
        def best_regression(y, x_dict):
            """
            Перебирает все комбинации X-переменных, находит лучшую структуру
            регрессионного уравнения по скорректированному R².

            Parameters
            ----------
            y : list[float]
                Зависимая переменная.
            x_dict : dict[str, list[float]]
                Словарь независимых переменных: {"name": [values...]}.

            Returns
            -------
            dict
                {
                    "variables": ["x1", "x3"],          # отобранные переменные
                    "coefficients": {"x1": 2.5, "x3": -1.1},  # коэффициенты при них
                    "intercept": 0.7,                   # свободный член
                    "r2": 0.92,                         # обычный R²
                    "r2_adjusted": 0.91,                # скорректированный R²
                    "equation": "y = 0.700 + 2.500*x1 + (-1.100)*x3",  # текст уравнения
                }
            """
            y = np.asarray(y, dtype=float)
            n = len(y)
            all_names = list(x_dict.keys())
            k_total = len(all_names)

            if n < 3:
                raise ValueError("Слишком мало наблюдений (нужно минимум 3)")

            # Проверка длин
            for name in all_names:
                if len(x_dict[name]) != n:
                    raise ValueError(f"Длина '{name}' не совпадает с длиной y ({n})")

            # Матрица всех X
            X_all = np.column_stack([np.asarray(x_dict[name], dtype=float) for name in all_names])

            best = None

            # Перебор всех комбинаций от 1 до k_total переменных
            for k in range(1, k_total + 1):
                for combo in combinations(range(k_total), k):
                    # print("best_regression calc  " ,combo)
                    X = X_all[:, list(combo)]
                    model = LinearRegression()
                    model.fit(X, y)

                    r2 = model.score(X, y)
                    # Скорректированный R²
                    if n - k - 1 > 0:
                        r2_adj = 1 - (1 - r2) * (n - 1) / (n - k - 1)
                    else:
                        r2_adj = -np.inf  # слишком много переменных при малом n

                    if best is None or r2_adj > best["r2_adjusted"]:
                        var_names = [all_names[i] for i in combo]
                        coefs = {var_names[i]: float(model.coef_[i]) for i in range(k)}
                        best = {
                            "variables": var_names,
                            "coefficients": coefs,
                            "intercept": float(model.intercept_),
                            "r2": float(r2),
                            "r2_adjusted": float(r2_adj),
                            "equation": Statistic.TimeSeriesAnalisys._build_equation(model.intercept_, var_names, model.coef_),
                        }

            return best

    class BUILD_MODEL:
        # ============================================================
        # 1. Построение признаков
        # ============================================================
        @staticmethod
        def _build_features(X: np.ndarray, kind: str) -> np.ndarray:
            """
            Формирует матрицу признаков для выбранной формы модели.
            Защищена от inf/nan, которые могут появиться при возведении
            больших биржевых цен в квадрат (poly2).
            """
            k = X.shape[1]

            if kind == "linear":
                return X

            if kind == "poly2":
                # Квадраты: чистим переполнение до того, как оно попортит всё дальше
                X2 = X ** 2
                if np.any(~np.isfinite(X2)):
                    X2 = np.nan_to_num(X2, nan=0.0, posinf=0.0, neginf=0.0)

                parts = [X, X2]

                # Взаимодействия x_i * x_j для i < j
                if k > 1:
                    interactions = []
                    for i, j in combinations(range(k), 2):
                        prod = X[:, i] * X[:, j]
                        if np.any(~np.isfinite(prod)):
                            prod = np.nan_to_num(prod, nan=0.0, posinf=0.0, neginf=0.0)
                        interactions.append(prod)
                    parts.append(np.column_stack(interactions))

                return np.hstack(parts)

            raise ValueError(f"Неизвестная форма: {kind}")

        # ============================================================
        # 2. Устойчивый решатель (каскад: solve -> lstsq -> pinv)
        # ============================================================
        @staticmethod
        def _solve_stable(A: np.ndarray, y: np.ndarray, lam: float = 1e-6) -> np.ndarray:
            """
            МНК с регуляризацией. Не падает при вырожденности:
              1) solve с нарастающей регуляризацией (lam * 100, до 8 раз);
              2) lstsq (SVD — устойчив к вырожденности);
              3) pinv — крайний рубеж.
            Всегда возвращает конечный вектор коэффициентов.
            """
            p = A.shape[1]

            # 1) Нормальные уравнения с адаптивной регуляризацией
            cur_lam = lam
            for _ in range(8):
                try:
                    AtA = A.T @ A + cur_lam * np.eye(p)
                    Aty = A.T @ y
                    coef = np.linalg.solve(AtA, Aty)
                    if np.all(np.isfinite(coef)):
                        return coef
                except np.linalg.LinAlgError:
                    pass
                cur_lam *= 100.0

            # 2) lstsq — не бросает исключений на вырожденной матрице
            try:
                coef, *_ = np.linalg.lstsq(A, y, rcond=None)
                if np.all(np.isfinite(coef)):
                    return coef
            except np.linalg.LinAlgError:
                pass

            # 3) Псевдообратная — последний рубеж
            coef = np.linalg.pinv(A) @ y
            return np.nan_to_num(coef, nan=0.0, posinf=0.0, neginf=0.0)

        # ============================================================
        # 3. Чистка данных от NaN/inf
        # ============================================================
        @staticmethod
        def _clean_finite(X: np.ndarray, y: np.ndarray):
            """
            Убирает строки с NaN/inf — главная причина ошибки
            «ни одна форма не решилась». Возвращает очищенные X и y.
            """
            ok = np.isfinite(y)
            ok &= np.all(np.isfinite(X), axis=1)
            return X[ok], y[ok]

        # ============================================================
        # 4. Подбор лучшей многомерной регрессии
        # ============================================================
        @staticmethod
        def bestMultivariateRegression(y, x_list, shift: int = 1, lam: float = 1e-6):
            """
            Подбирает лучшую функциональную форму многомерной регрессии
            для предсказания y в следующий момент времени.

            x_list можно передать двумя способами:
              1) список 1D-массивов: [x1, x2, x3] — ряды (выравниваются по хвосту);
              2) 2D-массив (n, k): строки — наблюдения, столбцы — переменные.

            Возвращает dict с моделью и методами predict/predict_next,
            либо {'error': 'причина'}. Никогда не падает с ошибкой
            «ни одна форма не решилась» — вместо этого возвращает
            константную модель-фоллбек.
            """
            y = np.asarray(y, dtype=float).ravel()
            if y.ndim != 1:
                return {"error": "y должен быть одномерным"}

            # --- Распознаём формат входа ---
            as_matrix = isinstance(x_list, np.ndarray) and x_list.ndim == 2
            if as_matrix:
                X_full = np.asarray(x_list, dtype=float)
                if X_full.shape[0] < len(y):
                    y = y[-X_full.shape[0]:]
                L_full = min(X_full.shape[0], len(y))
                X_full = X_full[-L_full:]
                y_al = y[-L_full:]
                k = X_full.shape[1]
            else:
                if not x_list or len(x_list) == 0:
                    return {"error": "x_list пуст"}
                lens = [len(np.asarray(x, dtype=float).ravel()) for x in x_list]
                L_full = min(len(y), min(lens))
                if L_full < 5:
                    return {"error": f"слишком мало точек после выравнивания: L={L_full} (< 5)"}
                y_al = y[-L_full:]
                cols = [np.asarray(x, dtype=float).ravel()[-L_full:] for x in x_list]
                X_full = np.column_stack(cols)
                k = X_full.shape[1]

            if L_full < 5:
                return {"error": f"слишком мало точек: L={L_full} (< 5)"}

            # --- Сдвиг: y_{t+shift} ~ f(x_t) ---
            X_fit = X_full[:-shift]
            y_fit = y_al[shift:]
            n = len(y_fit)
            if n < 5:
                return {"error": f"после сдвига осталось {n} наблюдений (< 5)"}

            # --- Чистка: выбрасываем строки с NaN/inf ---
            X_fit, y_fit = Statistic.BUILD_MODEL._clean_finite(X_fit, y_fit)
            n = len(y_fit)
            if n < 3:
                # Вырожденный фоллбек: константная модель — среднее по y
                mean_y = float(np.nanmean(y_al))
                return {
                    "model_name": "constant", "r2": 0.0, "adj_r2": 0.0,
                    "params": [mean_y],
                    "formula": f"y_(t+{shift}) ~ const={mean_y:.4g}",
                    "n_obs": n, "n_feat": k,
                    "tried": [("все формы", "данные вырождены (NaN/inf)")],
                    "predict": lambda xv: mean_y,
                    "predict_next": lambda: mean_y,
                }

            # --- Нормализация признаков ---
            # Убирает переполнение X^2 и плохую обусловленность матрицы
            mu = X_fit.mean(axis=0)
            sigma = X_fit.std(axis=0)
            sigma[sigma < 1e-12] = 1.0  # константные столбцы не трогаем
            Xn_fit = (X_fit - mu) / sigma

            # --- Кандидаты-формы ---
            forms = ["linear"]
            n_params_poly2 = 1 + k + k + k * (k - 1) // 2
            if n_params_poly2 <= max(n // 5, k + 2):
                forms.append("poly2")

            best = None
            tried = []
            F = None  # матрица признаков лучшей формы (нужна для predict)

            for form in forms:
                # --- Построение признаков ---
                try:
                    F_cur = Statistic.BUILD_MODEL._build_features(Xn_fit, form)
                except Exception as e:
                    tried.append((form, f"ошибка признаков: {e}"))
                    continue

                # --- Безопасная фильтрация вырожденных столбцов ---
                # keep всегда считается заново и строго по текущему F_cur,
                # поэтому ошибка "boolean index did not match" исключена
                if F_cur.shape[0] > 1:
                    col_std = F_cur.std(axis=0)
                    col_std = np.nan_to_num(col_std, nan=0.0, posinf=0.0, neginf=0.0)
                    keep_cur = col_std > 1e-12
                else:
                    keep_cur = np.ones(F_cur.shape[1], dtype=bool)

                # Гарантия согласованности размеров
                if keep_cur.shape[0] != F_cur.shape[1]:
                    keep_cur = np.ones(F_cur.shape[1], dtype=bool)

                if not keep_cur.all():
                    F_cur = F_cur[:, keep_cur]

                A = np.column_stack([np.ones(n), F_cur])

                # --- Решение ---
                try:
                    coef = Statistic.BUILD_MODEL._solve_stable(A, y_fit, lam)
                except Exception as e:
                    tried.append((form, f"не решается: {e}"))
                    continue

                y_pred = A @ coef

                ss_res = float(np.sum((y_fit - y_pred) ** 2))
                ss_tot = float(np.sum((y_fit - y_fit.mean()) ** 2))
                r2 = 1 - ss_res / ss_tot if ss_tot > 1e-30 else 0.0
                r2 = max(-1.0, min(r2, 1.0))  # защита от численного мусора
                p = A.shape[1]
                adj_r2 = 1 - (1 - r2) * (n - 1) / (n - p - 1) if n - p - 1 > 0 else r2
                tried.append((form, f"r2={r2:.4f}"))

                if best is None or adj_r2 > best[0]:
                    best = (adj_r2, r2, form, coef)
                    F = F_cur
                    keep = keep_cur

            # --- Фоллбек: если вообще ничего не решилось ---
            if best is None:
                mean_y = float(np.mean(y_fit))
                return {
                    "model_name": "constant", "r2": 0.0, "adj_r2": 0.0,
                    "params": [mean_y],
                    "formula": f"y_(t+{shift}) ~ const={mean_y:.4g}",
                    "n_obs": n, "n_feat": k, "tried": tried,
                    "predict": lambda xv: mean_y,
                    "predict_next": lambda: mean_y,
                }

            adj_r2, r2, form, coef = best

            # --- Формула (в нормированных переменных z) ---
            names = ["const"] + [f"z{i + 1}" for i in range(F.shape[1])]
            terms = [f"{c:+.4g}*{nm}" for c, nm in zip(coef, names)]
            formula = f"y_(t+{shift}) ~ " + " ".join(terms[:8]) + (" ..." if len(terms) > 8 else "")

            # --- Функции прогноза ---
            def predict(x_vector):
                xv = np.asarray(x_vector, dtype=float).ravel()
                if xv.shape[0] != k:
                    raise ValueError(f"ожидался вектор длины {k}, получено {xv.shape[0]}")
                # Чистим входные данные (NaN/inf -> 0)
                xv = np.nan_to_num(xv, nan=0.0, posinf=0.0, neginf=0.0)
                # Та же нормализация, что при обучении
                xvn = (xv - mu) / sigma
                Fp = Statistic.BUILD_MODEL._build_features(xvn.reshape(1, -1), form)
                # Согласуем с маской столбцов, отобранной при обучении
                if Fp.shape[1] != F.shape[1]:
                    Fp = Fp[:, keep]
                A = np.column_stack([np.ones(1), Fp])
                return float((A @ coef).item())

            def predict_next():
                return predict(X_full[-1])

            return {
                "model_name": form,
                "r2": r2,
                "adj_r2": adj_r2,
                "params": coef.tolist(),
                "formula": formula,
                "n_obs": n,
                "n_feat": k,
                "tried": tried,
                # Сохраняем параметры нормализации и маску — можно восстановить
                # модель позже и безопасно считать прогнозы
                "mu": mu.tolist(),
                "sigma": sigma.tolist(),
                "keep_mask": keep.tolist(),
                "predict": predict,
                "predict_next": predict_next,
            }

        @staticmethod
        def buildModel(timeSeries):
            """
            The model includes lags values
            :return:

            Напиши одним методом поиск лучшей функциональной формы многомерной регрессии. На вход метод принимает массив значений целевой переменной и массив массивов объясняющих переменных. Метод должен помимо прочего возвращать метод описывающий ожидаемую в следующий момент времени у
            """
            relevantLagsData = Statistic.TimeSeriesAnalisys.StandartMethods.AutocorrelationResearch.getRelevantArrays(timeSeries)
            # print(";;;",Statistic.BUILD_MODEL.bestMultivariateRegression(timeSeries, relevantLagsData))
            return Statistic.BUILD_MODEL.bestMultivariateRegression(timeSeries, relevantLagsData)["predict_next"]()





