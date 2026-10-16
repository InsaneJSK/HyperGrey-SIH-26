"""Sequential V2 evidence capture, also used unchanged by the Kaggle notebook."""
import argparse,datetime,hashlib,json,math,os,platform,shutil,statistics,subprocess,sys,time
from pathlib import Path
import psutil
from benchmark_lp import ROOT,parse_json_output
from gpu_memory import GpuMemorySampler,connect_nvml
GPU_API,GPU_HANDLE,GPU_ERROR=connect_nvml()

def save(path,data):path.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def measured(command,timeout):
    began=time.perf_counter();peak=0;gpu_memory=GpuMemorySampler(GPU_API,GPU_HANDLE,GPU_ERROR)
    process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    monitor=psutil.Process(process.pid);timed_out=False
    while True:
        try:peak=max(peak,monitor.memory_info().rss)
        except psutil.Error:pass
        gpu_memory.sample(process.pid)
        if time.perf_counter()-began>timeout:
            process.kill();timed_out=True
        try:stdout,stderr=process.communicate(timeout=.02);break
        except subprocess.TimeoutExpired:continue
    try:data=parse_json_output(stdout)
    except ValueError:data={'status':'process_error','stdout':stdout,'stderr':stderr}
    if timed_out:data['status']='external_timeout'
    data.update(process_seconds=time.perf_counter()-began,peak_rss_sampled_bytes=peak,exit_code=process.returncode)
    data.update(gpu_memory.report())
    if stderr:data['stderr']=stderr
    return data

def main(args):
    if args.repeats<1 or args.limit<=0 or args.scale_limit<=0 or any(n<2 or n>2000000 for n in args.sizes):raise ValueError('Positive limits/repetitions and valid sizes are required')
    output=args.output.resolve();output.mkdir(parents=True,exist_ok=False)
    build=(ROOT/args.build).resolve();suffix='.exe' if os.name=='nt' else ''
    cli=build/('solver_cli'+suffix);scale=build/('solver_scale'+suffix)
    if not cli.exists():raise RuntimeError('Build the solver first')
    # The preserved V1 generators use this executable spelling on both OSes.
    (ROOT/'build').mkdir(exist_ok=True)
    alias=ROOT/'build/solver_cli.exe'
    if alias.resolve()!=cli.resolve():shutil.copy2(cli,alias)
    metadata={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'platform':platform.platform(),'processor':platform.processor(),
      'physical_cores':psutil.cpu_count(logical=False),'logical_cores':psutil.cpu_count(),'ram_bytes':psutil.virtual_memory().total,
      'python':sys.version,'compiler':subprocess.check_output(['g++','--version'],text=True).splitlines()[0],
      'binary_sha256':sha(cli),'scale_binary_sha256':sha(scale),'time_limit_seconds':args.limit,'mip_nodes':10000,
      'cmake_sha256':sha(ROOT/'CMakeLists.txt'),'cmake_cache_sha256':sha(build/'CMakeCache.txt'),
      'memory_protocol':'RSS sampled every 20ms; excludes descendants; a lower bound on true peak',
      'gpu_memory_protocol':'Optional NVML device 0; process bytes require a matching PID; separately labeled device-wide samples can include other users/processes/driver allocations; failures are recorded, never converted to zero',
      'gpu_memory_initialization_error':GPU_ERROR,
      'source_sha256':{str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for folder in ['src','include','tests','scripts','docs'] for p in sorted((ROOT/folder).rglob('*')) if p.suffix in ('.cpp','.hpp','.cu','.py','.ps1','.md')},
      'gpu_requested':args.cuda,'gpu_result_status':'pending' if args.cuda else 'not_run_no_cuda_requested'}
    if shutil.which('nvidia-smi'):
        gpu=subprocess.run(['nvidia-smi'],capture_output=True,text=True);metadata['nvidia_smi']=gpu.stdout+gpu.stderr
    save(output/'metadata.json',metadata)
    shutil.copy2(build/'CMakeCache.txt',output/'CMakeCache.txt')
    ctest=subprocess.run(['ctest','--test-dir',str(build),'--output-on-failure'],capture_output=True,text=True)
    (output/'ctest.log').write_text(ctest.stdout+ctest.stderr)
    if ctest.returncode:raise RuntimeError('C++ regression checks failed; see ctest.log')
    certificate_tests=subprocess.run([sys.executable,str(ROOT/'scripts/test_qp_certificate.py')],capture_output=True,text=True)
    (output/'qp_certificate_tests.log').write_text(certificate_tests.stdout+certificate_tests.stderr)
    if certificate_tests.returncode:raise RuntimeError('Independent QP certificate checks failed')
    import test_generated,test_milp,test_qp,test_mixed_v2,test_qp_equalities
    test_generated.main(output/'generated-lp');test_milp.main(output/'generated-milp',True);test_qp.main(output/'generated-qp',True);test_mixed_v2.main(output/'generated-mixed')
    test_qp_equalities.main(output/'generated-qp-equalities',cli)
    groups={}
    for name,file in [('generated_lp','generated-lp/summary.json'),('generated_milp','generated-milp/enumeration.json'),('generated_qp','generated-qp/generated.json'),('generated_mixed','generated-mixed/summary.json'),('generated_qp_equalities','generated-qp-equalities/summary.json')]:
        entries=json.loads((output/file).read_text());groups[name]={'passed':sum(bool(r['passed']) for r in entries),'total':len(entries)}
    cases=[]
    for family,extension,milp in [('netlib','.mps',False),('miplib','.mps',True),('qplib','.qplib',False),('miplib2017','.mps',True)]:
        manifest=ROOT/'datasets'/family/'manifest.json'
        if not manifest.exists():continue
        for spec in json.loads(manifest.read_text())['instances']:
            model=ROOT/'datasets'/family/(spec['name']+extension)
            if model.exists():cases.append((family,spec['name'],model,milp,spec.get('mps_sha256',spec.get('model_sha256'))))
    for spec in json.loads((ROOT/'examples/industrial/manifest.json').read_text()):cases.append(('industrial',spec['name'],ROOT/'examples/industrial'/(spec['name']+'.mps'),spec['milp'],spec['sha256']))
    records=[]
    for family,name,model,milp,expected_hash in cases:
        if expected_hash and sha(model)!=expected_hash:raise RuntimeError('Dataset hash changed: '+str(model))
        folder=output/family;folder.mkdir(exist_ok=True)
        command=[str(cli),str(model),'--json','--time-limit',str(args.limit)]
        if milp:command+=['--milp']
        ours=measured(command,args.limit+10);candidate=folder/(name+'.ours.json');save(candidate,ours)
        qp=model.suffix=='.qplib'
        reference=ROOT/'scripts'/('reference_qp.py' if qp else 'benchmark_lp.py')
        refmodel=model.with_suffix('.lp') if qp else model
        reference_result=measured([sys.executable,str(reference),'--reference',str(refmodel),'--candidate',str(candidate),'--limit',str(args.limit)],args.limit+20)
        save(folder/(name+'.reference.json'),reference_result)
        actual,expected=ours.get('objective'),reference_result.get('objective')
        error=abs(actual-expected)/(1+abs(expected)) if actual is not None and expected is not None else None
        recomputed=reference_result.get('candidate_recomputed_objective')
        consistent=actual is not None and recomputed is not None and abs(actual-recomputed)/(1+abs(actual))<=1e-7
        passed=(ours.get('status') in ('optimal','gap_limit') and reference_result.get('status')=='Optimal' and error is not None and error<=1e-6 and consistent and reference_result.get('candidate_scaled_violation',math.inf)<=(1e-7 if qp else 1e-8) and reference_result.get('candidate_integer_violation',0)<=1e-7)
        if not milp:passed=passed and ours.get('optimality_verified') is True
        record={'family':family,'name':name,'passed':bool(passed),'status':ours.get('status'),'reference_status':reference_result.get('status'),
          'objective':actual,'reference_objective':expected,'relative_error':error,'seconds':ours.get('total_seconds'),'process_seconds':ours.get('process_seconds'),
          'peak_rss_sampled_bytes':ours['peak_rss_sampled_bytes'],'rows':ours.get('rows'),'columns':ours.get('columns'),'nodes':ours.get('nodes'),'gap':ours.get('gap'),
          'warm_starts':ours.get('warm_starts'),'cuts':ours.get('cuts'),'source_sha256':sha(model),
          'pump_projections':ours.get('pump_projections'),'pump_incumbents':ours.get('pump_incumbents'),
          'cut_rollbacks':ours.get('cut_rollbacks'),
          'first_incumbent_seconds':ours.get('first_incumbent_seconds')}
        if qp:
            certificate=reference_result.get('candidate_certificate',{})
            record['independent_kkt_passed']=certificate.get('independent_kkt_passed',False)
            record['independent_diagonal_certificate_passed']=certificate.get('diagonal_certificate_passed',False)
            record['independent_relative_dual_gap']=certificate.get('relative_dual_gap')
        records.append(record);save(output/'benchmarks.json',records);print(family,name,record['status'],'PASS' if passed else 'INCOMPLETE',flush=True)
    performance=[]
    for size in args.sizes:
        for backend,threads in [('cpu',1),('cpu',min(4,psutil.cpu_count(logical=False) or 1))]+([('cuda',1)] if args.cuda else []):
            for repetition in range(args.repeats):
                record=measured([str(scale),str(size),backend,str(threads),str(args.scale_limit)],args.scale_limit+20)
                record.update(requested_columns=size,requested_backend=backend,requested_threads=threads,repetition=repetition)
                performance.append(record);save(output/'scale.json',performance)
                print('scale',size,backend,threads,repetition,record.get('status'),flush=True)
    for family in sorted({r['family'] for r in records}):
        selected=[r for r in records if r['family']==family];groups[family]={'passed':sum(r['passed'] for r in selected),'total':len(selected)}
    qp_cases=[r for r in records if r['family']=='qplib']
    groups['qplib_independent_kkt']={'passed':sum(r.get('independent_kkt_passed',False) for r in qp_cases),'total':len(qp_cases)}
    groups['scale']={'passed':sum(bool(r.get('passed')) for r in performance),'total':len(performance)}
    summary={'groups':groups,'all_generated_passed':all(g['passed']==g['total'] for name,g in groups.items() if name.startswith('generated')),
      'all_public_cases_completed':all(r['passed'] for r in records),'gpu_verified':args.cuda and all(r.get('passed') for r in performance if r['requested_backend']=='cuda'),
      'known_limitations':['Small selected public sets, not complete libraries','GPU implementation covers convex box QPs','MIQP/NLP/MINLP remain extension targets','Mittelmann benchmark-set runs remain pending','Sampled memory can miss short-lived peaks']}
    save(output/'summary.json',summary)
    metadata['gpu_result_status']='verified_on_selected_cases' if summary['gpu_verified'] else ('failed_checks' if args.cuda else 'not_run_no_cuda_requested');save(output/'metadata.json',metadata)
    lines=['# V2 validation evidence','',f"Generated correctness: {'PASS' if summary['all_generated_passed'] else 'FAIL'}.",'','| Group | Passed | Total |','| --- | ---: | ---: |']
    lines += [f"| {name} | {g['passed']} | {g['total']} |" for name,g in groups.items()]
    lines+=['','The qplib group still requires an independently optimal reference result. The separate qplib_independent_kkt group checks returned primal/dual vectors on the original QPLIB data; strict diagonal models additionally report a separable Lagrangian bound and numerical gap in benchmarks.json and reference JSON. No reference timeout is relabeled as a reference pass.','', 'All incomplete public cases remain in benchmarks.json. Scale cases are synthetic tridiagonal convex box QPs with planted solutions; they do not establish general million-variable industrial capability.','', 'GPU status: '+metadata['gpu_result_status']+'.','', 'Timing includes setup, transfer and solution checks inside the solver; process time also includes startup. All scale repetitions run sequentially. RSS is sampled, not an exact peak.']
    (output/'REPORT.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(summary,indent=2),flush=True)
    return 0 if summary['all_generated_passed'] and groups['scale']['passed']==groups['scale']['total'] else 1

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);parser.add_argument('--build',default='build-v2');parser.add_argument('--limit',type=float,default=30);parser.add_argument('--cuda',action='store_true');parser.add_argument('--sizes',type=int,nargs='+',default=[10000,100000]);parser.add_argument('--repeats',type=int,default=3);parser.add_argument('--scale-limit',type=float,default=120)
    sys.exit(main(parser.parse_args()))
