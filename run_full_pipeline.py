"""
Master script to run the entire project pipeline
"""
import subprocess
import sys
from pathlib import Path

def run_script(script_path, description):
    """Run a Python script"""
    print("\n" + "="*70)
    print(f"RUNNING: {description}")
    print("="*70)
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            check=True,
            capture_output=False
        )
        print(f"✓ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed with error code {e.returncode}")
        return False
    except Exception as e:
        print(f"✗ {description} failed: {str(e)}")
        return False

def main():
    """Run complete pipeline"""
    print("="*70)
    print("RUNNING COMPLETE PROJECT PIPELINE")
    print("="*70)
    print("\nThis will run all scripts in order:")
    print("1. Data ingestion (prices, news, reddit)")
    print("2. Label creation")
    print("3. Feature engineering (technical, sentiment, AI-index)")
    print("4. Model training (baselines, boosting)")
    print("5. Meta-labeling gate")
    print("6. Backtesting")
    print("7. SHAP analysis")
    print("8. Visualizations")
    print("\nThis may take 30-60 minutes...")
    
    input("\nPress Enter to continue or Ctrl+C to cancel...")
    
    scripts = [
        ("src/data_ingestion/price_data.py", "Price Data Ingestion"),
        ("src/data_ingestion/news_data.py", "News Data Ingestion"),
        ("src/data_ingestion/reddit_data.py", "Reddit Data Ingestion"),
        ("src/data_ingestion/create_labels.py", "Label Creation"),
        ("src/features/technical.py", "Technical Features"),
        ("src/features/sentiment.py", "Sentiment Features"),
        ("src/features/ai_index.py", "AI-Intensity Index"),
        ("src/models/baselines.py", "Baseline Models"),
        ("src/models/boosting.py", "Boosting Models"),
        ("src/models/meta_gate.py", "Meta-Labeling Gate"),
        ("src/evaluation/backtester.py", "Backtesting"),
        ("src/evaluation/shap_analysis.py", "SHAP Analysis"),
        ("src/evaluation/create_all_visualizations.py", "Visualizations"),
    ]
    
    results = {}
    
    for script_path, description in scripts:
        success = run_script(script_path, description)
        results[description] = success
        
        if not success:
            print(f"\n⚠️  Pipeline stopped at: {description}")
            user_input = input("Continue anyway? (y/n): ")
            if user_input.lower() != 'y':
                break
    
    # Print summary
    print("\n" + "="*70)
    print("PIPELINE SUMMARY")
    print("="*70)
    
    for description, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status:8s} - {description}")
    
    all_success = all(results.values())
    
    if all_success:
        print("\n🎉 COMPLETE PROJECT PIPELINE FINISHED!")
        print("\nNext steps:")
        print("1. Review results in results/tables/")
        print("2. View figures in results/figures/")
        print("3. Run: python generate_final_report.py")
    else:
        completed = sum(results.values())
        total = len(results)
        print(f"\n⚠️  Pipeline partially completed: {completed}/{total} steps")
    
    return all_success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline cancelled by user")
        sys.exit(1)