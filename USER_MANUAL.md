# User Manual

## Introduction

This manual will walk you through every feature of the Semiconductor Yield Prediction & Optimization System. Whether you're a process engineer looking to optimize your fab line or a data scientist exploring yield patterns, this guide has you covered.

## AI Models Used

The system leverages advanced AI models for intelligent analysis:

**Primary Model: Mistral-7B-Instruct**
- A 7-billion parameter language model accessed via HuggingFace Inference API
- Used by the Prediction Agent for sophisticated yield forecasting
- Understands complex relationships between process parameters and yield outcomes
- Provides nuanced analysis beyond simple statistical patterns

**Fallback: Rule-Based Algorithm**
- Sophisticated heuristic-based prediction system
- Automatically used when API key is not configured or API is unavailable
- Ensures the system always works, regardless of API availability
- Uses domain knowledge encoded in the system

**Optimization: Grid Search Algorithm**
- Systematic exploration of parameter space
- Tests combinations of temperature, etch time, and exposure dose
- Selects optimal parameters based on predicted yield

*For detailed model documentation, see [MODELS_USED.md](MODELS_USED.md)*

## Understanding the Interface

When you first open the system, you'll see a clean 3-column layout:

**Left Column - Upload Dataset**
This is where you manage your data. Upload new datasets, view existing ones, and keep everything organized.

**Middle Column - Yield Analysis & Optimization**
This is your workspace. Select datasets, adjust parameters, and run analyses here.

**Right Column - Prediction Results**
Results appear here after you run an analysis. Charts, metrics, recommendations - everything you need to make decisions.

## Working with Datasets

### Uploading a Dataset

The system accepts JSON and CSV files. Here's how to upload:

1. **Prepare Your File**
   - JSON files should contain an array of objects or a single object
   - CSV files should have headers in the first row
   - Make sure your data includes relevant fields (wafer_id, temperature, defect_density, etc.)

2. **Upload Process**
   - Click "Choose File" in the Upload Dataset section
   - Select your file (JSON or CSV only - PDFs are for reports, not input)
   - Optionally enter a dataset name (or leave empty to auto-detect from filename)
   - Click "Upload Dataset"

3. **What Happens Next**
   - The system validates your file
   - Data is stored securely
   - The dataset appears in your "Available Datasets" list
   - It's automatically selected for analysis

### Dataset Format

The system is flexible with data formats. It looks for common field names and maps them intelligently:

**Wafer Data Fields:**
- `wafer_id` or `waferId` - Identifier for the wafer
- `total_dies` or `totalDies` - Total number of dies
- `good_dies` or `goodDies` - Number of good dies
- `defect_density` or `defectDensity` - Defect density value

**Process Parameters:**
- `temperature` or `temp` - Process temperature
- `etch_time` or `etchTime` - Etch time in seconds
- `exposure_dose` or `exposureDose` - Exposure dose in mJ/cm²

**Metrology Data:**
- `thickness_mean` or `thicknessMean` - Mean thickness
- `thickness_std` or `thicknessStd` - Thickness standard deviation
- `cd_target` or `cdTarget` - Critical dimension target
- `cd_actual` or `cdActual` - Actual critical dimension

Don't have all these fields? No problem. The system uses intelligent defaults and works with whatever data you have.

### Managing Datasets

**Viewing Datasets:**
- All uploaded datasets appear in the "Available Datasets" section
- You can see the name, row count, column count, and upload date
- Click "Refresh List" to update the list

**Selecting a Dataset:**
- Use the dropdown in the Yield Analysis section
- Select any dataset from the list
- The form will automatically populate with data from that dataset

**Deleting a Dataset:**
- Click the red "Delete" button next to any dataset
- Confirm the deletion
- The dataset is removed from the system

## Running Yield Analysis

### Step-by-Step Analysis

1. **Select Your Dataset**
   - Choose a dataset from the dropdown
   - The form fields will populate automatically
   - Review the values - you can edit them if needed

2. **Review Process Parameters**
   - **Temperature** - Your process temperature in °C
   - **Etch Time** - Etch duration in seconds
   - **Exposure Dose** - Lithography exposure dose in mJ/cm²
   
   Adjust these if you want to test different scenarios.

3. **Check Wafer Data**
   - **Wafer ID** - Identifier for tracking
   - **Total Dies** - Total number of dies on the wafer
   - **Good Dies** - Number of functional dies
   - **Defect Density** - Defect density measurement

4. **Verify Metrology Data**
   - **Thickness Mean/Std** - Film thickness measurements
   - **CD Target/Actual** - Critical dimension measurements

5. **Run Analysis**
   - Click the purple "🚀 Analyze Yield" button
   - Wait a few seconds while the multi-agent system processes your data
   - Results appear in the right column

### Understanding the Results

**Predicted Yield Card:**
- Shows your current predicted yield percentage
- Includes a confidence level (how certain the system is)
- Based on your current process parameters

**Optimized Yield Card:**
- Shows the potential yield with optimized parameters
- Displays the improvement percentage
- This is what you could achieve with recommended changes

**Yield Comparison Chart:**
- Visual bar chart comparing current vs optimized yield
- Easy to see the potential improvement at a glance

**Optimized Parameters:**
- Shows the recommended values for:
  - Temperature
  - Etch Time
  - Exposure Dose
- These are the settings that would give you the optimized yield

**Recommendations:**
- Actionable advice in plain language
- Each recommendation includes:
  - What to change
  - Why to change it
  - Expected improvement
  - Current vs recommended values

## Generating PDF Reports

After running an analysis, you can generate a professional PDF report:

1. **Click "Download PDF Report"**
   - The green button at the bottom of the results section
   - Wait a few seconds for generation

2. **What's in the Report:**
   - Executive summary
   - Detailed yield prediction analysis
   - Parameter optimization results
   - Actionable recommendations
   - Multi-agent system status
   - Professional formatting suitable for presentations

3. **Using the Report:**
   - Share with stakeholders
   - Include in documentation
   - Use for process improvement meetings
   - Archive for compliance

## Tips for Best Results

**Data Quality Matters:**
- The more complete your data, the better the predictions
- Include all relevant process parameters
- Accurate metrology data improves recommendations

**Experiment with Parameters:**
- Try different parameter combinations
- Compare multiple analyses
- Use the system to explore "what-if" scenarios

**Review Recommendations Carefully:**
- Recommendations are based on AI analysis
- Consider your specific process constraints
- Validate recommendations with your process knowledge

**Use Multiple Datasets:**
- Upload datasets from different process runs
- Compare results across different conditions
- Build a knowledge base of optimizations

## Troubleshooting

**Upload Fails:**
- Check that your file is JSON or CSV format
- Ensure the file isn't corrupted
- Try a smaller file if the upload times out

**Analysis Takes Too Long:**
- Large datasets may take longer
- Check your backend server is running
- Refresh the page if it seems stuck

**Results Don't Appear:**
- Check browser console for errors (F12)
- Verify backend is running on port 8006
- Ensure frontend is running on port 3008

**Form Doesn't Populate:**
- Make sure you selected a dataset from the dropdown
- Check that your dataset has valid data
- Try refreshing the dataset list

## Advanced Usage

**Batch Analysis:**
- Upload multiple datasets
- Run analyses on each one
- Compare results across different conditions

**Parameter Exploration:**
- Manually adjust parameters
- Run multiple analyses
- Find optimal settings through experimentation

**Data Integration:**
- Export results to other tools
- Use PDF reports in presentations
- Integrate with your existing workflow

## Getting Support

If you encounter issues:
1. Check that both servers are running
2. Verify your data format is correct
3. Review the error messages in the browser console
4. Check the backend logs for detailed error information

Remember, this system is designed to be intuitive, but if you need help, the error messages are usually quite descriptive and will point you in the right direction.

Happy optimizing!

