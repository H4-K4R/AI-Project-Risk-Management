# 🔧 Troubleshooting Guide

## Common Issues and Solutions

---

## Installation Issues

### Issue 1: "Python is not recognized"
**Symptoms:** PowerShell says `python : The term 'python' is not recognized`

**Solutions:**
1. Install Python from https://www.python.org/downloads/
2. During installation, check "Add Python to PATH"
3. Restart PowerShell after installation
4. Verify: `python --version`

---

### Issue 2: "Cannot activate virtual environment"
**Symptoms:** `.\venv\Scripts\Activate.ps1` gives execution policy error

**Solution:**
```powershell
# Option 1: Set execution policy for current session
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# Then activate
.\venv\Scripts\Activate.ps1

# Option 2: Use full path
& "$PWD\venv\Scripts\Activate.ps1"
```

---

### Issue 3: "pip install fails"
**Symptoms:** Errors during `pip install -r requirements.txt`

**Solutions:**
```powershell
# Update pip first
python -m pip install --upgrade pip

# Install with verbose output to see errors
pip install -r requirements.txt --verbose

# Install packages individually if needed
pip install crewai
pip install streamlit
pip install pandas plotly
```

---

## API and Configuration Issues

### Issue 4: "HuggingFace API Error / Invalid API Key"
**Symptoms:** Analysis fails with API key error

**Solutions:**

1. **Check .env file exists:**
   ```powershell
   Get-Content .env
   ```

2. **Verify API key format:**
   - Should start with `hf_`
   - No quotes around the key
   - No extra spaces
   - Get token from: https://huggingface.co/settings/tokens

   **Correct:**
   ```env
   HF_API_TOKEN=hf_abc123def456...
   HF_MODEL=moonshotai/Kimi-K2-Instruct-0905
   ```

   **Incorrect:**
   ```env
   HF_API_TOKEN="hf_abc123def456..."  # Remove quotes
   OPENAI_API_KEY= sk-proj-abc123def456...   # Remove space
   ```

3. **Test API key:**
   ```python
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   key = os.getenv("OPENAI_API_KEY")
   print(f"Key found: {key is not None}")
   print(f"Key length: {len(key) if key else 0}")
   ```

4. **Get new API key:**
   - Go to https://platform.openai.com/api-keys
   - Create new secret key
   - Copy and paste into .env file

---

### Issue 5: "Rate limit exceeded"
**Symptoms:** API returns 429 error

**Solutions:**
- Wait a few minutes and try again
- Check your OpenAI account usage at https://platform.openai.com/usage
- Add credits to your account if needed
- For testing, use smaller datasets

---

## CSV Data Issues

### Issue 6: "CSV parsing error"
**Symptoms:** Error when uploading CSV file

**Common Causes & Fixes:**

1. **Missing columns:**
   - Ensure all required columns exist:
     `Task_ID`, `Task_Name`, `Duration_Days`, `Resource_Name`, `Cost_Per_Day`, `Predecessors`, `Risk_Level`

2. **Wrong Risk_Level values:**
   - Must be exactly: `Low`, `Med`, or `High` (case-sensitive)
   - Not: "low", "HIGH", "Medium", "H"

3. **Invalid Predecessors format:**
   - Leave blank or use comma-separated IDs
   - Correct: `1,2,3` or empty
   - Incorrect: `1 2 3`, `1-2`, `none`

4. **Special characters in Task_Name:**
   - Use quotes if name contains commas:
   ```csv
   5,"Design, Development, Testing",10,John,500,,Med
   ```

5. **Excel issues:**
   - Save as "CSV (Comma delimited)" not "CSV UTF-8"
   - Use "Save As" not just "Save"

**Test your CSV:**
```python
import pandas as pd
df = pd.read_csv("your_file.csv")
print(df.columns.tolist())  # Check columns
print(df['Risk_Level'].unique())  # Check risk values
print(df.isnull().sum())  # Check for missing data
```

---

## Streamlit Issues

### Issue 7: "Port already in use"
**Symptoms:** `Address already in use` when starting Streamlit

**Solutions:**
```powershell
# Option 1: Use different port
streamlit run app.py --server.port 8502

# Option 2: Kill existing Streamlit process
Get-Process -Name streamlit | Stop-Process -Force

# Then restart
streamlit run app.py
```

---

### Issue 8: "Streamlit page won't load"
**Symptoms:** Browser shows "Can't reach this page"

**Solutions:**
1. Check if Streamlit is actually running (should see output in terminal)
2. Try different browser
3. Clear browser cache
4. Go directly to http://localhost:8501
5. Check firewall isn't blocking port 8501

---

### Issue 9: "Session state error"
**Symptoms:** Errors about session_state

**Solution:**
```powershell
# Restart Streamlit with cache cleared
streamlit run app.py --server.enableCORS false
```

---

## Agent Execution Issues

### Issue 10: "Agents running forever / timeout"
**Symptoms:** Analysis never completes

**Possible Causes:**
1. Large dataset (>100 tasks)
2. API slowness
3. Network issues

**Solutions:**
```powershell
# Check if process is stuck
# Ctrl+C to stop in PowerShell

# Try with smaller dataset first
# Use first 10 rows of CSV to test

# Increase timeout in agents.py (if needed)
# Look for any timeout parameters
```

---

### Issue 11: "Tool execution failed"
**Symptoms:** Agent can't use tools

**Solutions:**
1. Verify CSV file path is correct
2. Check file permissions
3. Ensure CSV is not open in Excel
4. Try absolute path instead of relative

**Debug code:**
```python
import os
csv_path = "dummy_data.csv"
print(f"File exists: {os.path.exists(csv_path)}")
print(f"Absolute path: {os.path.abspath(csv_path)}")
```

---

## Import Errors

### Issue 12: "No module named 'X'"
**Symptoms:** ImportError when running scripts

**Solutions:**
```powershell
# Ensure virtual environment is activated
# You should see (venv) in prompt

# Verify activation
Get-Command python | Select-Object Source
# Should show path in venv folder

# If not activated
.\venv\Scripts\Activate.ps1

# Reinstall missing package
pip install <package_name>
```

---

### Issue 13: "Cannot import name 'X' from 'Y'"
**Symptoms:** Specific function/class can't be imported

**Solutions:**
```powershell
# Update package to latest version
pip install --upgrade <package_name>

# Or specific version from requirements.txt
pip install -r requirements.txt --force-reinstall
```

---

## Performance Issues

### Issue 14: "Dashboard is slow"
**Symptoms:** UI is laggy or unresponsive

**Solutions:**
1. Reduce dataset size (test with 10-20 tasks first)
2. Close other applications
3. Use Chrome/Edge (better Streamlit performance)
4. Disable browser extensions
5. Check if antivirus is scanning Python

---

### Issue 15: "Out of memory"
**Symptoms:** System crashes or freezes

**Solutions:**
```powershell
# Increase Python memory (Windows)
$env:PYTHONHASHSEED=0

# Use smaller datasets
# Process in chunks if needed
```

---

## Testing and Verification

### Issue 16: "How do I know it's working?"
**Solution:** Run the test suite

```powershell
# Activate venv first
.\venv\Scripts\Activate.ps1

# Run tests
python test_system.py
```

**Expected output:**
```
✓ pandas imported successfully
✓ streamlit imported successfully
...
Total: 6/6 test suites passed
🎉 All tests passed!
```

---

## Getting Help

### Step-by-step debugging process:

1. **Check basics:**
   - Python installed and in PATH?
   - Virtual environment activated?
   - All files present?

2. **Run test suite:**
   ```powershell
   python test_system.py
   ```

3. **Check error message:**
   - Read the full error (scroll up in terminal)
   - Note the file and line number
   - Copy exact error message

4. **Verify configuration:**
   - .env file has valid API key
   - CSV file format is correct
   - All dependencies installed

5. **Test components individually:**
   ```powershell
   # Test agents only
   python agents.py
   
   # Test CSV loading
   python -c "import pandas as pd; print(pd.read_csv('dummy_data.csv'))"
   ```

---

## Emergency Reset

### If everything is broken:

```powershell
# 1. Delete virtual environment
Remove-Item -Recurse -Force venv

# 2. Recreate environment
python -m venv venv

# 3. Activate
.\venv\Scripts\Activate.ps1

# 4. Update pip
python -m pip install --upgrade pip

# 5. Reinstall everything
pip install -r requirements.txt

# 6. Verify .env
Get-Content .env

# 7. Run tests
python test_system.py

# 8. Try again
streamlit run app.py
```

---

## Still Having Issues?

### Collect diagnostic information:

```powershell
# Python version
python --version

# Package versions
pip list

# Current directory
Get-Location

# Files present
Get-ChildItem

# Environment variables
Get-Content .env

# Test import
python -c "import crewai; import streamlit; import pandas; print('All imports OK')"
```

Send this information when asking for help.

---

## Quick Reference Commands

```powershell
# Setup
.\setup.ps1

# Activate environment
.\venv\Scripts\Activate.ps1

# Run application
streamlit run app.py

# Run tests
python test_system.py

# Test agents only
python agents.py

# Update packages
pip install --upgrade -r requirements.txt

# Deactivate environment
deactivate
```

---

## Success Checklist

Before running the application, verify:

- [ ] Python 3.10+ installed
- [ ] Virtual environment created and activated
- [ ] All packages from requirements.txt installed
- [ ] .env file exists with valid OPENAI_API_KEY
- [ ] dummy_data.csv file present and readable
- [ ] test_system.py passes all tests
- [ ] No error messages in terminal

If all checked ✓, you're ready to run:
```powershell
streamlit run app.py
```

---

**Last updated:** 2025-12-09
