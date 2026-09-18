import numpy as np
        from numpy.polynomial import Polynomial

class Statistic:
    class Regressions:
        def bestRegression(x, y, max_degree=5, folds=5, random_state=42):
            """
            Ищет лучшую среди линейной, экспоненциальной и полиномиальных регрессий.

            Parameters
            ----------
            x, y : array-like
                Массивы одинаковой длины с исходными данными.
            max_degree : int
                Максимальная степень полинома.
            folds : int
                Количество фолдов для cross-validation.
            random_state : int
                Seed для воспроизводимого перемешивания данных.

            Returns
            -------
            dict:
                {
                    "model": "linear" | "exponential" | "polynomial",
                    "degree": int | None,
                    "coefficients": [...],
                    "formula": str,
                    "cv_rmse": float,
                    "all_scores": {...}
                }

            Форматы коэффициентов:
              linear:
                  [k, b], где y = k*x + b

              exponential:
                  [a, b], где y = a*exp(b*x)

              polynomial:
                  [cN, ..., c1, c0], где
                  y = cN*x^N + ... + c1*x + c0
            """

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

            # При CV в каждом обучающем наборе должно хватать точек
            max_test_size = int(np.ceil(len(x) / folds))
            min_train_size = len(x) - max_test_size
            allowed_max_degree = min(max_degree, min_train_size - 1)

            if allowed_max_degree < 1:
                raise ValueError("Недостаточно данных для построения регрессии.")

            # Описание кандидатов
            candidates = [("linear", 1)]

            for degree in range(2, allowed_max_degree + 1):
                candidates.append(("polynomial", degree))

            # Для логарифмирования y в экспоненциальной модели нужны только y > 0
            if np.all(y > 0):
                candidates.append(("exponential", None))

            def fit_model(model_type, degree, x_train, y_train):
                if model_type == "exponential":
                    # log(y) = log(a) + b*x
                    b, log_a = np.polyfit(x_train, np.log(y_train), 1)
                    a = np.exp(log_a)
                    return np.array([a, b])

                # Polynomial.fit устойчивее, чем прямой np.polyfit для больших x.
                # convert() переводит результат в обычный базис степеней x.
                poly = Polynomial.fit(x_train, y_train, degree).convert()

                # Polynomial хранит [c0, c1, ..., cN],
                # а возвращаем привычный порядок [cN, ..., c1, c0].
                return poly.coef[::-1]

            def predict(model_type, coefficients, x_values):
                if model_type == "exponential":
                    a, b = coefficients
                    with np.errstate(over="raise", invalid="raise"):
                        return a * np.exp(b * x_values)

                return np.polyval(coefficients, x_values)

            # Разбиваем индексы на фолды
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

            # Модель с минимальным CV RMSE
            best_name = min(scores, key=scores.get)

            if best_name == "linear":
                best_type, best_degree = "linear", 1
            elif best_name == "exponential":
                best_type, best_degree = "exponential", None
            else:
                best_type = "polynomial"
                best_degree = int(best_name.split("_")[1])

            # Дообучаем победителя на всех данных
            best_coefficients = fit_model(best_type, best_degree, x, y)

            if best_type == "linear":
                formula = "y = k*x + b"
            elif best_type == "exponential":
                formula = "y = a * exp(b*x)"
            else:
                formula = f"y = c{best_degree}*x^{best_degree} + ... + c1*x + c0"

            return {
                "model": best_type,
                "degree": best_degree,
                "coefficients": best_coefficients.tolist(),
                "formula": formula,
                # "cv_rmse": scores[best_name],
                # "all_scores": scores
            }

        def calculateRegressionNumbers(self, x, y):
            print(self.bestRegression(x, y))
            buf = []
            match bestRegression(x, y)['model']:
                case "linear":
                    for i in x:
                        coefs = bestRegression(x  , y)['coefficients']
                        buf.append(coefs[0] * i + coefs[1])
                case "polynomial":
                    match bestRegression(x, y)['degree']:
                        case 3:
                            for i in x:
                                coefs = bestRegression(x  , y)['coefficients']
                                buf.append(coefs[0] * i ** 3 + coefs[1] * i ** 2 + coefs[2] * i ** 1 + coefs[3])

                    ax.plot(x , buf, 'o', color='red', label=f'Asks apps')