import os

files = ['1_requests.py',
         '2_session.py',
         '3_async1.py',
         '5_async3.py',
         '6_action1.py',
         '7_action2.py']

for _ in range(100):
    for file in files:
        print(f'\nStarting script {file}')
        os.system(f'python3 {file}')
        print(f'Ending script {file}\n')
