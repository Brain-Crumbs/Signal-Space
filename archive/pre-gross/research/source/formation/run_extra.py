from run_checks import add,run,root
import run_checks,concurrent.futures
run_checks.jobs.clear()
for w in [1,2]:
 for nu in [.6,1.3]:add(f'unbound_w{w}_n{nu}',w=w,nu=nu)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 for r in pool.map(run,run_checks.jobs):print(r,flush=True)
