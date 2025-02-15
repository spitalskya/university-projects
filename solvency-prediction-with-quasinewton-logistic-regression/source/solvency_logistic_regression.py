import warnings
import pandas as pd
import matplotlib.pyplot as plt
from logistic_regression import LogisticRegression


def main() -> None:
    """Run logistic regression for every method and step size.
    For each save coefficients, percentage of correct predictions and visualize convergence.
    """
    
    # load data
    train_data = pd.read_csv("data/credit_risk_train.csv")
    u_train, v_train = train_data.drop("Creditability", axis="columns").to_numpy(), train_data["Creditability"].to_numpy()
    test_data = pd.read_csv("data/credit_risk_test.csv")
    u_test = test_data.drop("Creditability", axis="columns").to_numpy()
    v_real = test_data["Creditability"].to_numpy()
    
    # suppress `RuntimeWarning: overflow encountered in exp` warnings (we were not able to resolve them)
    warnings.filterwarnings("ignore")
    with open("solvency_log_reg_results/results.txt", "w") as results:
        results.write(f"{"method":<11}{"step":<13}{"time":<10}{"correct predictions":<22}{"coefficients"}\n")
        for method, step in zip(
                ["BFGS", "BFGS", "DFP", "DFP", "Cauchy", "Grad-Const"],
                ["suboptimal", "optimal", "suboptimal", "optimal", "", ""]
            ):
                log_reg = LogisticRegression()
                log_reg.fit(u=u_train, v=v_train, method=method, step=step, time_minimization=True)
                
                fig, ax = plt.subplots()
                log_reg.visualize(ax)
                ax.set_title(
                    f"Convergence graph - " +
                    f"{method} method " +
                    f"{f"with {step} step" if step else ""}"
                    )
                fig.savefig(f"solvency_log_reg_results/{method}{"_" + step if step else ""}.png")
                
                v_pred = log_reg.predict(u_test)
                count_predicted_correctly: int = 0
                for i in range(len(v_real)):
                    if v_real[i] == v_pred[i]:
                        count_predicted_correctly += 1
                        
                results.write(f"{method:<11}{f"{step}" if step else "":<13}" +
                              f"{round(log_reg.minimization_time, 4):<10}" +
                              f"{round(count_predicted_correctly / len(v_real), 8):<22}" +
                              f"{log_reg.coefficients}\n")


if __name__ == "__main__":
    main()
