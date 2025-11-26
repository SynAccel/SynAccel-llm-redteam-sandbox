import matplotlib.pyplot as plt


def plot_security_timeline(risk_scores):
    """
    Creates a visual graph of risk scores over time
    """

    x = list(range(1, len(risk_scores) + 1))  # Message numbers
    y = risk_scores  # Risk levels (0–100)

    plt.figure()
    plt.plot(x, y, marker='o')
    plt.title("Security Risk Timeline")
    plt.xlabel("Message Number")
    plt.ylabel("Risk Level (0–100)")
    plt.ylim(0, 100)
    plt.show()
