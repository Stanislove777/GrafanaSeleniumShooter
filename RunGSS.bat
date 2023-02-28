chcp 65001
set src_path=GSS.py
set drv_path="chromedriver_win32/chromedriver.exe"
set host="http://localhost:3000"
set dashboard="mydashboardtest"
set dir="Run_1688"
set rows="RowSecond" "RowFirst"
set time_start="27.02.2023 19:00:00"
set time_end="27.02.2023 20:00:00"

python -m pip install -r .\requirements.txt
python %src_path% --host %host% --username "admin" --password "admin" --drv_path %drv_path% --org_id "1" --storage_dir %dir% --dashboard %dashboard% --rows %rows% --time_range_start %time_start% --time_range_end %time_end%
pause