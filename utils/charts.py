import logging
import os
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime

logger = logging.getLogger(__name__)

# Use non-interactive backend for server environments
matplotlib.use("Agg")


def plot_sentiment(positive: int, negative: int, neutral: int, 
                   filename: str = "sentiment.png", output_dir: str = "outputs") -> str:
    """
    Create bar chart of sentiment distribution.
    
    Args:
        positive (int): Count of positive sentiments
        negative (int): Count of negative sentiments
        neutral (int): Count of neutral sentiments
        filename (str): Output filename
        output_dir (str): Output directory
        
    Returns:
        str: Full path to saved image
        
    Raises:
        Exception: If plotting fails
    """
    try:
        logger.info(f"Generating sentiment chart: pos={positive}, neg={negative}, neu={neutral}")
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"Created output directory: {output_dir}")
        
        # Clear previous plots
        plt.clf()
        plt.close("all")
        
        # Create bar chart
        fig, ax = plt.subplots(figsize=(10, 6))
        
        labels = ["Positive", "Negative", "Neutral"]
        values = [positive, negative, neutral]
        colors = ["#2ecc71", "#e74c3c", "#95a5a6"]
        
        bars = ax.bar(labels, values, color=colors, alpha=0.7, edgecolor="black")
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                f"{int(height)}",
                ha="center",
                va="bottom",
                fontweight="bold"
            )
        
        # Customize chart
        ax.set_ylabel("Count", fontsize=12, fontweight="bold")
        ax.set_title("Sentiment Analysis Results", fontsize=14, fontweight="bold")
        ax.grid(axis="y", alpha=0.3, linestyle="--")
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        fig.text(0.99, 0.01, f"Generated: {timestamp}", 
                ha="right", va="bottom", fontsize=9, style="italic")
        
        # Save figure
        filepath = os.path.join(output_dir, filename)
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches="tight")
        logger.info(f"Sentiment chart saved to: {filepath}")
        
        return filepath
        
    except Exception as e:
        logger.error(f"Failed to generate sentiment chart: {str(e)}")
        raise
    finally:
        plt.close("all")


def plot_sentiment_timeline(sentiments: list, timestamps: list = None,
                           filename: str = "sentiment_timeline.png", 
                           output_dir: str = "outputs") -> str:
    """
    Create timeline chart of sentiment progression.
    
    Args:
        sentiments (list): List of sentiment values or labels
        timestamps (list): Optional timestamps for x-axis
        filename (str): Output filename
        output_dir (str): Output directory
        
    Returns:
        str: Full path to saved image
    """
    try:
        logger.info(f"Generating sentiment timeline with {len(sentiments)} data points")
        
        if not sentiments:
            logger.warning("No sentiment data provided")
            raise ValueError("Sentiments list cannot be empty")
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        plt.clf()
        plt.close("all")
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Convert sentiment labels to numeric values
        sentiment_values = []
        for s in sentiments:
            if isinstance(s, str):
                if s.lower() == "positive":
                    sentiment_values.append(1)
                elif s.lower() == "negative":
                    sentiment_values.append(-1)
                else:
                    sentiment_values.append(0)
            else:
                sentiment_values.append(s)
        
        # Create x-axis
        x_axis = timestamps if timestamps else range(len(sentiment_values))
        
        # Plot
        ax.plot(x_axis, sentiment_values, marker="o", linestyle="-", 
               linewidth=2, markersize=6, color="#3498db")
        ax.axhline(y=0, color="gray", linestyle="--", alpha=0.5)
        
        # Colors for background
        ax.fill_between(range(len(sentiment_values)), 0, 1, 
                        where=[v > 0 for v in sentiment_values],
                        alpha=0.2, color="green", label="Positive")
        ax.fill_between(range(len(sentiment_values)), -1, 0,
                        where=[v < 0 for v in sentiment_values],
                        alpha=0.2, color="red", label="Negative")
        
        # Customize
        ax.set_ylabel("Sentiment Score", fontsize=12, fontweight="bold")
        ax.set_xlabel("Time", fontsize=12, fontweight="bold")
        ax.set_title("Sentiment Timeline", fontsize=14, fontweight="bold")
        ax.legend()
        ax.grid(True, alpha=0.3, linestyle="--")
        
        # Save
        filepath = os.path.join(output_dir, filename)
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches="tight")
        logger.info(f"Timeline chart saved to: {filepath}")
        
        return filepath
        
    except Exception as e:
        logger.error(f"Failed to generate sentiment timeline: {str(e)}")
        raise
    finally:
        plt.close("all")


def create_report(analysis_results: dict, output_dir: str = "outputs") -> str:
    """
    Create a comprehensive analysis report.
    
    Args:
        analysis_results (dict): Results from analysis pipeline
        output_dir (str): Output directory
        
    Returns:
        str: Path to report file
    """
    try:
        import json
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Create report filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(output_dir, f"report_{timestamp}.json")
        
        with open(report_path, "w") as f:
            json.dump(analysis_results, f, indent=2)
        
        logger.info(f"Report saved to: {report_path}")
        return report_path
        
    except Exception as e:
        logger.error(f"Failed to create report: {str(e)}")
        raise