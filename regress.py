import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score

def best_regression(x, y):
    """Сравнивает линейную, экспоненциальную и полиномиальные регрессии, возвращает коэффициенты лучшей по R²."""
    x = np.array(x).reshape(-1, 1)
    y = np.array(y)
    models = {}

    # Линейная регрессия
    lin = LinearRegression().fit(x, y)
    models['linear'] = (lin.coef_[0], lin.intercept_, r2_score(y, lin.predict(x)))

    # Экспоненциальная (a*e^(b*x) + c)
    def exp_func(x, a, b, c):
        return a * np.exp(b * x) + c
    try:
        popt, _ = curve_fit(exp_func, x.flatten(), y, maxfev=5000)
        y_pred = exp_func(x.flatten(), *popt)
        models['exponential'] = (*popt, r2_score(y, y_pred))
    except:
        pass

    # Полиномы 2 и 3 степени
    for degree in [2, 3]:
        poly = PolynomialFeatures(degree)
        x_poly = poly.fit_transform(x)
        model = LinearRegression().fit(x_poly, y)
        y_pred = model.predict(x_poly)
        models[f'poly_{degree}'] = (model.coef_, model.intercept_, r2_score(y, y_pred))

    best = max(models, key=lambda k: models[k][-1])
    return best, models[best][0]
