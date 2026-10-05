import numpy as np
from matplotlib import pyplot as plt


class DataCombinations:
    params_1_power = {}
    params_2_power = {}
    params_3_power = {}
    params_E_in_power = {}

    params = {}

    def __init__(self, db):
        DataCombinations.params_1_power = {"spread                       ": db.get_history_columns(["spread"])["spread"],
                          "regression_area_ratio        ": db.get_history_columns(["regression_area_ratio"])[
                              "regression_area_ratio"],
                          "rectangle_area_ratio         ": db.get_history_columns(["rectangle_area_ratio"])[
                              "rectangle_area_ratio"],
                          "regression_coeff_ratio       ": db.get_history_columns(["regression_coeff_ratio"])[
                              "regression_coeff_ratio"],
                          "points_above_regression_ratio": db.get_history_columns(["points_above_regression_ratio"])[
                              "points_above_regression_ratio"],
                          "asks_third1_count            ": db.get_history_columns(["asks_third1_count"])[
                              "asks_third1_count"],
                          "asks_third2_count            ": db.get_history_columns(["asks_third2_count"])[
                              "asks_third2_count"],
                          "asks_third3_count            ": db.get_history_columns(["asks_third3_count"])[
                              "asks_third3_count"],
                          "bids_third1_count            ": db.get_history_columns(["bids_third1_count"])[
                              "bids_third1_count"],
                          "bids_third2_count            ": db.get_history_columns(["bids_third2_count"])[
                              "bids_third2_count"],
                          "bids_third3_count            ": db.get_history_columns(["bids_third3_count"])[
                              "bids_third3_count"], }
        DataCombinations.params_2_power = {"spread**2                       ": np.array(db.get_history_columns(["spread"])[
                                                                           "spread"]) ** 2,
                          "regression_area_ratio**2         ":
                              np.array(db.get_history_columns(["regression_area_ratio"])[
                                           "regression_area_ratio"]) ** 2,
                          "rectangle_area_ratio**2          ":
                              np.array(db.get_history_columns(["rectangle_area_ratio"])[
                                           "rectangle_area_ratio"]) ** 2,
                          "regression_coeff_ratio**2        ":
                              np.array(db.get_history_columns(["regression_coeff_ratio"])[
                                           "regression_coeff_ratio"]) ** 2,
                          "points_above_regression_ratio)**2 ":
                              np.array(db.get_history_columns(["points_above_regression_ratio"])[
                                           "points_above_regression_ratio"]) ** 2,
                          "asks_third1_count**2             ":
                              np.array(db.get_history_columns(["asks_third1_count"])[
                                           "asks_third1_count"]) ** 2,
                          "asks_third2_count**2             ":
                              np.array(db.get_history_columns(["asks_third2_count"])[
                                           "asks_third2_count"]) ** 2,
                          "asks_third3_count**2             ":
                              np.array(db.get_history_columns(["asks_third3_count"])[
                                           "asks_third3_count"]) ** 2,
                          "bids_third1_count**2          ":
                              np.array(db.get_history_columns(["bids_third1_count"])[
                                           "bids_third1_count"]) ** 2,
                          "bids_third2_count**2          ":
                              np.array(db.get_history_columns(["bids_third2_count"])[
                                           "bids_third2_count"]) ** 2,
                          "bids_third3_count**2           ":
                              np.array(db.get_history_columns(["bids_third3_count"])[
                                           "bids_third3_count"]) ** 2, }
        DataCombinations.params_3_power = {"spread**3                       ": np.array(db.get_history_columns(["spread"])[
                                                                           "spread"]) ** 3,
                          "regression_area_ratio**3         ":
                              np.array(db.get_history_columns(["regression_area_ratio"])[
                                           "regression_area_ratio"]) ** 3,
                          "rectangle_area_ratio**3          ":
                              np.array(db.get_history_columns(["rectangle_area_ratio"])[
                                           "rectangle_area_ratio"]) ** 3,
                          "regression_coeff_ratio**3        ":
                              np.array(db.get_history_columns(["regression_coeff_ratio"])[
                                           "regression_coeff_ratio"]) ** 3,
                          "points_above_regression_ratio)**3 ":
                              np.array(db.get_history_columns(["points_above_regression_ratio"])[
                                           "points_above_regression_ratio"]) ** 3,
                          "asks_third1_count**3             ":
                              np.array(db.get_history_columns(["asks_third1_count"])[
                                           "asks_third1_count"]) ** 3,
                          "asks_third2_count**3             ":
                              np.array(db.get_history_columns(["asks_third2_count"])[
                                           "asks_third2_count"]) ** 3,
                          "asks_third3_count**3             ":
                              np.array(db.get_history_columns(["asks_third3_count"])[
                                           "asks_third3_count"]) ** 3,
                          "bids_third1_count**3          ":
                              np.array(db.get_history_columns(["bids_third1_count"])[
                                           "bids_third1_count"]) ** 3,
                          "bids_third2_count**3          ":
                              np.array(db.get_history_columns(["bids_third2_count"])[
                                           "bids_third2_count"]) ** 3,
                          "bids_third3_count**3           ":
                              np.array(db.get_history_columns(["bids_third3_count"])[
                                           "bids_third3_count"]) ** 3}
        DataCombinations.params_E_in_power = {
            "spread e^                       ": np.exp(np.array(db.get_history_columns(["spread"])[
                                                             "spread"])),
            "regression_area_ratio e^         ":
                np.exp(np.array(db.get_history_columns(["regression_area_ratio"])[
                             "regression_area_ratio"])),
            "rectangle_area_ratio e^          ":
                np.exp(np.array(db.get_history_columns(["rectangle_area_ratio"])[
                             "rectangle_area_ratio"])),
            "regression_coeff_ratio e^        ":
                np.exp(np.array(db.get_history_columns(["regression_coeff_ratio"])[
                             "regression_coeff_ratio"])),
            "points_above_regression_ratio) e^ ":
                np.exp(np.array(db.get_history_columns(["points_above_regression_ratio"])[
                             "points_above_regression_ratio"])),
            "asks_third1_count e^             ":
                np.exp(np.array(db.get_history_columns(["asks_third1_count"])[
                             "asks_third1_count"])),
            "asks_third2_count e^             ":
                np.exp(np.array(db.get_history_columns(["asks_third2_count"])[
                             "asks_third2_count"])),
            "asks_third3_count e^             ":
                np.exp(np.array(db.get_history_columns(["asks_third3_count"])[
                             "asks_third3_count"])),
            "bids_third1_count e^          ":
                np.exp(np.array(db.get_history_columns(["bids_third1_count"])[
                             "bids_third1_count"])),
            "bids_third2_count e^          ":
                np.exp(np.array(db.get_history_columns(["bids_third2_count"])[
                             "bids_third2_count"])),
            "bids_third3_count e^           ":
                np.exp(np.array(db.get_history_columns(["bids_third3_count"])[
                             "bids_third3_count"]))}

        DataCombinations.params = (
                DataCombinations.params_1_power |
                DataCombinations.params_2_power |
                DataCombinations.params_3_power |
                DataCombinations.params_E_in_power
        )
        DataCombinations.check_overflow_candidates(DataCombinations.params)

    @staticmethod
    def check_overflow_candidates(params_dict):
        for name, arr in params_dict.items():
            arr = np.asarray(arr, dtype=float)
            if np.any(np.isinf(arr)) or np.any(np.isnan(arr)):
                print(f"[!] {name}: есть inf/nan, длина={len(arr)}, кол-во inf={np.sum(np.isinf(arr))}, кол-во nan={np.sum(np.isnan(arr))}")
            max_val = np.max(np.abs(arr))
            if max_val > 1e150:
                print(f"[!] {name}: очень большие значения, max={max_val:.3e}")

    @staticmethod
    def plot_all_features_vs_y(y_values, features_dict, y_name="Y", max_per_window=10):
        """
        Строит точечные графики для ВСЕХ признаков из словаря против y.
        Открывает несколько окон, по max_per_window графиков в каждом.

        Параметры:
            y_values: массив/список значений целевой переменной.
            features_dict: словарь {название_признака: массив_значений}.
            y_name: имя целевой переменной для подписей осей.
            max_per_window: максимум графиков в одном окне (по умолчанию 10).
        """
        y = np.asarray(y_values, dtype=float)

        # Очистка и подготовка данных
        clean_data = []

        for name, x_raw in features_dict.items():
            x = np.asarray(x_raw, dtype=float)
            if len(x) != len(y):
                continue

            mask = ~(np.isnan(x) | np.isnan(y) | np.isinf(x) | np.isinf(y))
            x_clean = x[mask]
            y_clean = y[mask]

            if len(x_clean) < 2:
                continue

            clean_data.append((name, x_clean, y_clean))

        if not clean_data:
            print("Нет валидных данных для построения графиков.")
            return

        total = len(clean_data)
        n_windows = (total + max_per_window - 1) // max_per_window  # ceil division

        print(f"Всего признаков: {total}, окон: {n_windows}")

        for win_idx in range(n_windows):
            start = win_idx * max_per_window
            end = min(start + max_per_window, total)
            batch = clean_data[start:end]

            n_plots = len(batch)
            cols = 2
            rows = (n_plots + 1) // 2

            fig, axes = plt.subplots(rows, cols, figsize=(14, 4 * rows))
            fig.suptitle(f'Окно {win_idx + 1} из {n_windows}: {y_name} (X) vs признаки (Y)',
                         fontsize=14, y=1.0)

            if n_plots == 1:
                axes = [axes]
            else:
                axes = axes.flatten()

            for idx, (name, x_clean, y_clean) in enumerate(batch):
                ax = axes[idx]

                # X = y (цель), Y = признак
                ax.scatter(y_clean, x_clean, color='#1f77b4', alpha=0.6, s=20,
                           edgecolors='white', linewidth=0.5, label='Данные')

                # Линия тренда
                try:
                    z = np.polyfit(y_clean, x_clean, 1)
                    p = np.poly1d(z)
                    ax.plot(y_clean, p(y_clean), 'r-', linewidth=2,
                            label=f'Тренд: y={z[0]:.3f}x+{z[1]:.3f}')
                except Exception:
                    pass

                short_name = name.strip().replace("**2", "²").replace("**3", "³").replace(" e^", "")
                ax.set_title(f'{short_name}', fontsize=10)
                ax.set_xlabel(y_name)
                ax.set_ylabel(short_name)
                ax.grid(True, linestyle='--', alpha=0.3)
                ax.legend(loc='best', fontsize=7)

            # Скрываем пустые подграфики
            for j in range(n_plots, len(axes)):
                fig.delaxes(axes[j])

            plt.tight_layout()

        # Показываем все окна сразу
        plt.show()
