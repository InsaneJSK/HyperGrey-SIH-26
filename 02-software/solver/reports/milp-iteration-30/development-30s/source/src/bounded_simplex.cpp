#include "bounded_simplex.hpp"
#include <algorithm>
#include <chrono>
#include <cmath>
#include <limits>
#include <numeric>
#include <stdexcept>
#include <cstdio>
#include <cstdlib>

namespace sovereign {
namespace {
const double kInf=std::numeric_limits<double>::infinity();
enum : std::uint8_t {kBasic=0,kLower=1,kUpper=2,kFree=3};

// Left-looking sparse LU (Gilbert-Peierls) of the basis with threshold
// partial pivoting, followed by product-form eta updates. B Q = L U, where
// column k of the factor is basis position qpos[k] and its pivot row prow[k].
class LuFactor {
public:
    int m=0;
    std::vector<int> prow,pinv,qpos,lstart,lidx,ustart,uidx,estart,eidx,erow;
    std::vector<double> lval,uval,udiag,eval,epiv;
    std::size_t eta_nonzeros=0,factor_nonzeros=0;
    mutable std::vector<double> scratch;
    std::vector<int> vis,rowmark,xi,stack,epos,cand,rowcount;
    int visstamp=0,rowstamp=0;

    int etas()const{return static_cast<int>(erow.size());}
    void clear_etas(){estart.assign(1,0);eidx.clear();eval.clear();erow.clear();epiv.clear();eta_nonzeros=0;}

    // False when some basis positions could not be pivoted; those are listed.
    bool factor(int size,const std::vector<int>& bs,const std::vector<int>& bi,const std::vector<double>& bv,std::vector<int>& singular) {
        m=size;int rank=0;
        prow.assign(m,-1);pinv.assign(m,-1);qpos.assign(m,-1);
        lstart.assign(1,0);lidx.clear();lval.clear();
        ustart.assign(1,0);uidx.clear();uval.clear();udiag.clear();
        clear_etas();
        scratch.assign(m,0.0);
        vis.assign(m,0);rowmark.assign(m,0);xi.assign(m,0);stack.assign(m,0);epos.assign(m,0);
        visstamp=rowstamp=0;
        rowcount.assign(m,0);
        for(int k=0;k<bs[m];++k)++rowcount[bi[k]];
        std::vector<int> order(m);std::iota(order.begin(),order.end(),0);
        std::stable_sort(order.begin(),order.end(),[&](int a,int b){return bs[a+1]-bs[a]<bs[b+1]-bs[b];});
        singular.clear();
        std::vector<double>& w=scratch;
        for(int pos:order) {
            ++visstamp;int top=m;
            for(int k=bs[pos];k<bs[pos+1];++k){int s=pinv[bi[k]];if(s>=0&&vis[s]!=visstamp)dfs(s,top);}
            ++rowstamp;cand.clear();double colmax=0;
            for(int k=bs[pos];k<bs[pos+1];++k){
                int r=bi[k];w[r]+=bv[k];colmax=std::max(colmax,std::abs(bv[k]));
                if(pinv[r]<0&&rowmark[r]!=rowstamp){rowmark[r]=rowstamp;cand.push_back(r);}
            }
            for(int p=top;p<m;++p){
                int s=xi[p];double v=w[prow[s]];if(v==0)continue;
                for(int e=lstart[s];e<lstart[s+1];++e){
                    int r=lidx[e];w[r]-=lval[e]*v;
                    if(pinv[r]<0&&rowmark[r]!=rowstamp){rowmark[r]=rowstamp;cand.push_back(r);}
                }
            }
            double best=0;for(int r:cand)best=std::max(best,std::abs(w[r]));
            if(!(best>1e-11*std::max(1.0,colmax))||!std::isfinite(best)) {
                singular.push_back(pos);
                for(int r:cand)w[r]=0;
                for(int p=top;p<m;++p)w[prow[xi[p]]]=0;
                continue;
            }
            int piv=-1;
            for(int r:cand){
                double a=std::abs(w[r]);
                if(a>=.1*best&&(piv<0||rowcount[r]<rowcount[piv]||(rowcount[r]==rowcount[piv]&&a>std::abs(w[piv]))))piv=r;
            }
            for(int p=top;p<m;++p){int s=xi[p];int r=prow[s];double v=w[r];if(v!=0){uidx.push_back(s);uval.push_back(v);}w[r]=0;}
            const double diag=w[piv];udiag.push_back(diag);
            for(int r:cand){
                if(r!=piv){double v=w[r]/diag;if(std::abs(v)>1e-14){lidx.push_back(r);lval.push_back(v);}}
                w[r]=0;
            }
            w[piv]=0;
            lstart.push_back(static_cast<int>(lidx.size()));ustart.push_back(static_cast<int>(uidx.size()));
            prow[rank]=piv;pinv[piv]=rank;qpos[rank]=pos;++rank;
        }
        factor_nonzeros=lidx.size()+uidx.size()+udiag.size();
        return singular.empty();
    }
    // Input indexed by row, output indexed by basis position (in place).
    void ftran(std::vector<double>& v)const {
        std::vector<double>& z=scratch;
        for(int s=0;s<m;++s){
            const double x=v[prow[s]];z[s]=x;
            if(x!=0)for(int e=lstart[s];e<lstart[s+1];++e)v[lidx[e]]-=lval[e]*x;
        }
        for(int k=m-1;k>=0;--k){
            double x=z[k];if(x==0)continue;
            x/=udiag[k];z[k]=x;
            for(int e=ustart[k];e<ustart[k+1];++e)z[uidx[e]]-=uval[e]*x;
        }
        for(int k=0;k<m;++k)v[qpos[k]]=z[k];
        for(std::size_t t=0;t<erow.size();++t){
            const int r=erow[t];const double x=v[r]/epiv[t];v[r]=x;
            if(x!=0)for(int e=estart[t];e<estart[t+1];++e)v[eidx[e]]-=eval[e]*x;
        }
    }
    // Input indexed by basis position, output indexed by row (in place).
    void btran(std::vector<double>& c)const {
        for(std::size_t t=erow.size();t-->0;){
            const int r=erow[t];long double s=c[r];
            for(int e=estart[t];e<estart[t+1];++e)s-=static_cast<long double>(eval[e])*c[eidx[e]];
            c[r]=static_cast<double>(s/epiv[t]);
        }
        std::vector<double>& g=scratch;
        for(int k=0;k<m;++k)g[k]=c[qpos[k]];
        for(int k=0;k<m;++k){
            double s=g[k];
            for(int e=ustart[k];e<ustart[k+1];++e)s-=uval[e]*g[uidx[e]];
            g[k]=s/udiag[k];
        }
        for(int s=m-1;s>=0;--s){
            double value=g[s];
            for(int e=lstart[s];e<lstart[s+1];++e)value-=lval[e]*c[lidx[e]];
            c[prow[s]]=value;
        }
    }
    // alpha is the position-indexed FTRAN of the entering column.
    void update(int r,const std::vector<double>& alpha) {
        erow.push_back(r);epiv.push_back(alpha[r]);
        for(int i=0;i<m;++i)if(i!=r&&std::abs(alpha[i])>1e-14){eidx.push_back(i);eval.push_back(alpha[i]);}
        estart.push_back(static_cast<int>(eidx.size()));eta_nonzeros=eidx.size();
    }
private:
    void dfs(int s0,int& top) {
        int head=0;stack[0]=s0;epos[0]=lstart[s0];vis[s0]=visstamp;
        while(head>=0){
            const int s=stack[head];bool descended=false;
            while(epos[head]<lstart[s+1]){
                const int r=lidx[epos[head]++];const int s2=pinv[r];
                if(s2>=0&&vis[s2]!=visstamp){vis[s2]=visstamp;++head;stack[head]=s2;epos[head]=lstart[s2];descended=true;break;}
            }
            if(!descended){xi[--top]=s;--head;}
        }
    }
};

struct Candidate {int j;double t,h,a;};

struct Engine {
    const LinearProblem& P;const BoundedLpModel& M;const Options& opt;BoundedLpStats& stats;
    const int n,m,N;
    std::chrono::steady_clock::time_point began=std::chrono::steady_clock::now();
    const double big=1e7;
    double ptol,dtol,pivtol=1e-9;
    std::vector<double> lo,up,tlo,tup,c,c0,x,d,dse;
    std::vector<std::uint8_t> status,artificial;
    std::vector<int> basic;
    LuFactor lu;
    std::vector<double> alpha,rho,alpha_row,tau,shift_rhs,farkas;
    std::vector<int> touched,mark,bs,bi,flip_list;
    std::vector<double> bv;
    std::vector<Candidate> cands;
    std::vector<double> hmin;
    int markv=0;
    std::vector<int> ignored;int ignore_stamp=1;std::size_t ignored_count=0;
    std::size_t iterations=0;
    bool shifted=false,any_artificial=false;
    double next_cutoff_check=-kInf;
    double cutoff_bound=-kInf;

    Engine(const LinearProblem& p,const BoundedLpModel& model,const Options& o,BoundedLpStats& s)
        :P(p),M(model),opt(o),stats(s),n(static_cast<int>(model.n)),m(static_cast<int>(model.m)),N(n+m) {
        ptol=opt.tolerance;dtol=opt.tolerance;
        mark.assign(N,0);alpha_row.assign(N,0.0);
    }
    bool expired()const{return std::chrono::duration<double>(std::chrono::steady_clock::now()-began).count()>=opt.time_limit_seconds;}
    template<class F> void for_column(int j,F&& f)const {
        if(j<n){for(int k=M.col_start[j];k<M.col_start[j+1];++k)f(M.col_index[k],M.col_value[k]);}
        else f(j-n,-1.0);
    }
    // Scaled tolerances derived per variable from ORIGINAL-space targets, so the
    // final unscaled checks see at most ptol/dtol-sized relative residuals.
    std::vector<double> ptl,ptu,dt;
    double range_factor(double lower_bound,double upper_bound)const{
        const double range=upper_bound-lower_bound;
        return std::isfinite(range)?std::max(1.0,std::min(range,1e9)):1.0;
    }

    void setup(const std::vector<double>& lower,const std::vector<double>& upper) {
        tlo.assign(N,-kInf);tup.assign(N,kInf);
        ptl.assign(N,ptol);ptu.assign(N,ptol);dt.assign(N,dtol);
        auto clamp=[](double v,double a,double b){return std::max(a,std::min(b,v));};
        for(int j=0;j<n;++j){
            const double S=M.col_scale[j];
            if(std::isfinite(lower[j]))tlo[j]=lower[j]/S;
            if(std::isfinite(upper[j]))tup[j]=upper[j]/S;
            ptl[j]=ptol*(1+std::min(1e6,std::isfinite(lower[j])?std::abs(lower[j]):0.0))/S;
            ptu[j]=ptol*(1+std::min(1e6,std::isfinite(upper[j])?std::abs(upper[j]):0.0))/S;
            dt[j]=clamp(dtol*(1+std::abs(P.cost[j]))*S/M.cost_scale/range_factor(lower[j],upper[j]),1e-12,1e-6);
        }
        for(int i=0;i<m;++i){
            const double R=M.row_scale[i];
            if(std::isfinite(P.row_lower[i]))tlo[n+i]=P.row_lower[i]*R;
            if(std::isfinite(P.row_upper[i]))tup[n+i]=P.row_upper[i]*R;
            ptl[n+i]=ptol*(1+std::min(1e6,std::isfinite(P.row_lower[i])?std::abs(P.row_lower[i]):0.0))*R;
            ptu[n+i]=ptol*(1+std::min(1e6,std::isfinite(P.row_upper[i])?std::abs(P.row_upper[i]):0.0))*R;
            dt[n+i]=clamp(dtol/(M.cost_scale*R)/range_factor(P.row_lower[i],P.row_upper[i]),1e-12,1e-6);
        }
        lo=tlo;up=tup;artificial.assign(N,0);
        c0.assign(N,0.0);for(int j=0;j<n;++j)c0[j]=M.cost[j];
        c=c0;x.assign(N,0.0);d.assign(N,0.0);dse.assign(m,1.0);
        status.assign(N,kLower);basic.assign(m,-1);
        ignored.assign(m,0);ignore_stamp=1;ignored_count=0;
    }
    void place_nonbasic(int j,std::uint8_t preferred) {
        const bool lf=std::isfinite(lo[j]),uf=std::isfinite(up[j]);
        std::uint8_t s=preferred;
        if(lo[j]==up[j])s=kLower;
        else if(s==kLower&&!lf)s=uf?kUpper:kFree;
        else if(s==kUpper&&!uf)s=lf?kLower:kFree;
        else if(s==kFree&&(lf||uf))s=lf?kLower:kUpper;
        status[j]=s;
        x[j]=s==kLower?lo[j]:(s==kUpper?up[j]:0.0);
    }
    void cold_start() {
        for(int j=0;j<n;++j)place_nonbasic(j,c0[j]>=0?kLower:kUpper);
        for(int i=0;i<m;++i){basic[i]=n+i;status[n+i]=kBasic;}
    }
    bool warm_start(const BoundedBasis& b) {
        if(b.structural!=static_cast<std::size_t>(n)||b.status.size()<static_cast<std::size_t>(n)||b.status.size()>static_cast<std::size_t>(N))return false;
        const int old=static_cast<int>(b.status.size());
        int count=0;
        for(int j=0;j<N;++j){
            std::uint8_t s=j<old?b.status[j]:kBasic;
            if(s>kFree)return false;
            if(s==kBasic){if(count>=m)return false;basic[count++]=j;status[j]=kBasic;x[j]=0;}
            else place_nonbasic(j,s);
        }
        return count==m;
    }
    bool refactor() {
        for(int attempt=0;attempt<4;++attempt){
            bs.assign(1,0);bi.clear();bv.clear();
            for(int pos=0;pos<m;++pos){
                for_column(basic[pos],[&](int i,double a){bi.push_back(i);bv.push_back(a);});
                bs.push_back(static_cast<int>(bi.size()));
            }
            std::vector<int> singular;
            ++stats.refactors;++ignore_stamp;ignored_count=0;
            if(lu.factor(m,bs,bi,bv,singular))return true;
            std::vector<int> free_rows;
            for(int i=0;i<m;++i)if(lu.pinv[i]<0)free_rows.push_back(i);
            if(free_rows.size()!=singular.size())return false;
            for(std::size_t k=0;k<singular.size();++k){
                const int pos=singular[k],j=basic[pos],r=free_rows[k];
                if(status[n+r]==kBasic)return false;
                basic[pos]=n+r;status[n+r]=kBasic;
                place_nonbasic(j,c[j]>=0?kLower:kUpper);
                ++stats.singular_repairs;
            }
        }
        return false;
    }
    void compute_primal() {
        std::vector<double>& v=alpha;v.assign(m,0.0);
        for(int j=0;j<N;++j){
            if(status[j]==kBasic||x[j]==0)continue;
            const double value=x[j];
            for_column(j,[&](int i,double a){v[i]-=a*value;});
        }
        lu.ftran(v);
        for(int pos=0;pos<m;++pos)x[basic[pos]]=v[pos];
    }
    void compute_dual() {
        std::vector<double>& y=rho;y.assign(m,0.0);
        for(int pos=0;pos<m;++pos)y[pos]=c[basic[pos]];
        lu.btran(y);
        for(int j=0;j<n;++j){
            if(status[j]==kBasic){d[j]=0;continue;}
            long double s=c[j];
            for(int k=M.col_start[j];k<M.col_start[j+1];++k)s-=static_cast<long double>(M.col_value[k])*y[M.col_index[k]];
            d[j]=static_cast<double>(s);
        }
        for(int i=0;i<m;++i)d[n+i]=status[n+i]==kBasic?0.0:c[n+i]+y[i];
    }
    bool dual_feasible(int j)const {
        if(status[j]==kBasic||lo[j]==up[j])return true;
        if(status[j]==kLower)return d[j]>=-dt[j];
        if(status[j]==kUpper)return d[j]<=dt[j];
        return std::abs(d[j])<=dt[j];
    }
    // Restore dual feasibility by bound flips; unbounded sides get a temporary
    // artificial bound that cleanup() removes before any result is accepted.
    bool make_dual_feasible() {
        bool changed=false;
        for(int j=0;j<N;++j){
            if(dual_feasible(j))continue;
            const double dj=d[j];
            if(status[j]==kLower||(status[j]==kFree&&dj<0)){
                if(!std::isfinite(up[j])){up[j]=(std::isfinite(lo[j])?lo[j]:0.0)+big;artificial[j]|=2;any_artificial=true;++stats.artificial;}
                status[j]=kUpper;x[j]=up[j];
            } else {
                if(!std::isfinite(lo[j])){lo[j]=(std::isfinite(up[j])?up[j]:0.0)-big;artificial[j]|=1;any_artificial=true;++stats.artificial;}
                status[j]=kLower;x[j]=lo[j];
            }
            changed=true;
        }
        if(changed)compute_primal();
        return changed;
    }
    bool reinvert() {
        if(!refactor())return false;
        compute_primal();compute_dual();make_dual_feasible();
        return true;
    }
    void compute_pivot_row(const std::vector<double>& y) {
        ++markv;touched.clear();
        for(int i=0;i<m;++i){
            const double yi=y[i];
            if(yi==0||std::abs(yi)<1e-14)continue;
            const int lj=n+i;
            if(status[lj]!=kBasic){
                if(mark[lj]!=markv){mark[lj]=markv;alpha_row[lj]=0;touched.push_back(lj);}
                alpha_row[lj]-=yi;
            }
            for(int k=M.row_start[i];k<M.row_start[i+1];++k){
                const int j=M.row_index[k];
                if(status[j]==kBasic)continue;
                if(mark[j]!=markv){mark[j]=markv;alpha_row[j]=0;touched.push_back(j);}
                alpha_row[j]+=yi*M.row_value[k];
            }
        }
    }
    double scaled_objective()const {
        long double z=0;for(int j=0;j<n;++j)if(x[j]!=0)z+=static_cast<long double>(c0[j])*x[j];
        return static_cast<double>(z);
    }
    // Row duals (scaled space) of the current basis, for any cost shifts.
    void current_duals(std::vector<double>& y)const {
        y.assign(m,0.0);
        for(int i=0;i<m;++i)y[i]=status[n+i]==kBasic?-c[n+i]:d[n+i]-c[n+i];
    }
    // Lagrangian bound valid for ANY multipliers: min c x >= sum_i y_i r_i + sum_j d_j x_j
    // over the true box, with d = c - A^T y recomputed from the original rows.
    double safe_bound(const std::vector<double>& yscaled,const std::vector<double>& lower,const std::vector<double>& upper)const {
        std::vector<long double> dj(n),mag(n);
        for(int j=0;j<n;++j){dj[j]=M.sense*P.cost[j];mag[j]=std::abs(P.cost[j]);}
        long double bound=M.offset,scale=1+std::abs(M.offset);
        for(int i=0;i<m;++i){
            const long double yi=static_cast<long double>(yscaled[i])*M.row_scale[i]*M.cost_scale;
            if(yi==0)continue;
            for(auto a:P.rows[i]){long double t=yi*a.second;dj[a.first]-=t;mag[a.first]+=std::abs(t);}
            const double side=yi>0?P.row_lower[i]:P.row_upper[i];
            if(std::isfinite(side)){bound+=yi*side;scale+=std::abs(yi*side);}
            else if(std::abs(yi)>1e-11*(1+std::abs(yi)))return -kInf;
        }
        for(int j=0;j<n;++j){
            const long double v=dj[j];if(v==0)continue;
            const double side=v>0?lower[j]:upper[j];
            if(std::isfinite(side)){bound+=v*side;scale+=std::abs(v*side);}
            else if(std::abs(v)>1e-11*(1+mag[j]))return -kInf;
        }
        const long double margin=4*std::numeric_limits<double>::epsilon()*scale;
        return static_cast<double>(bound-margin);
    }
    // Farkas check of a dual ray on the ORIGINAL rows and bounds.
    bool verify_farkas(const std::vector<double>& ray,const std::vector<double>& lower,const std::vector<double>& upper)const {
        std::vector<long double> g(n,0),mag(n,0);
        long double low=0,high=0,scale=0;int low_inf=0,high_inf=0;
        auto add=[&](long double coefficient,long double magnitude,double lb,double ub){
            if(coefficient==0)return;
            const double at_low=coefficient>0?lb:ub,at_high=coefficient>0?ub:lb;
            const bool negligible=std::abs(coefficient)<=1e-12*(1+magnitude);
            if(std::isfinite(at_low)){low+=coefficient*at_low;scale+=std::abs(coefficient*at_low);}else if(!negligible)++low_inf;
            if(std::isfinite(at_high)){high+=coefficient*at_high;scale+=std::abs(coefficient*at_high);}else if(!negligible)++high_inf;
        };
        // The certificate is homogeneous: normalize it so the margin is relative.
        long double largest=0;
        for(int i=0;i<m;++i)largest=std::max(largest,std::abs(static_cast<long double>(ray[i])*M.row_scale[i]));
        if(!(largest>0)||!std::isfinite(static_cast<double>(largest)))return false;
        for(int i=0;i<m;++i){
            const long double yi=static_cast<long double>(ray[i])*M.row_scale[i]/largest;
            if(yi==0)continue;
            for(auto a:P.rows[i]){long double t=yi*a.second;g[a.first]+=t;mag[a.first]+=std::abs(t);}
            add(-yi,std::abs(yi),P.row_lower[i],P.row_upper[i]);
        }
        for(int j=0;j<n;++j)add(g[j],mag[j],lower[j],upper[j]);
        const long double margin=1e-9*(1+scale);
        if(std::getenv("SOVEREIGN_BOUNDED_DEBUG"))std::fprintf(stderr,"farkas low=%g high=%g low_inf=%d high_inf=%d scale=%g\n",double(low),double(high),low_inf,high_inf,double(scale));
        return (!low_inf&&low>margin)||(!high_inf&&high<-margin);
    }

    // Dual phase with bound-flipping Harris ratio test and dual steepest edge.
    std::string dual_phase(double cutoff,const std::vector<double>& lower,const std::vector<double>& upper) {
        for(;;){
            if(expired())return "time_limit";
            if(iterations>=opt.iteration_limit)return "iteration_limit";
            int r=-1;double best=0;
            for(int pos=0;pos<m;++pos){
                if(ignored[pos]==ignore_stamp)continue;
                const int j=basic[pos];const double v=x[j];double infeasibility=0;
                if(v<lo[j]-ptl[j])infeasibility=lo[j]-v;
                else if(v>up[j]+ptu[j])infeasibility=v-up[j];
                if(infeasibility>0){const double score=infeasibility*infeasibility/dse[pos];if(score>best){best=score;r=pos;}}
            }
            if(r<0)return ignored_count?"ignored_rows":"optimal";
            if(!std::isfinite(best))return "numerical_error";
            const int p=basic[r];
            const bool to_lower=x[p]<lo[p];
            const double target=to_lower?lo[p]:up[p];
            double delta=x[p]-target;
            rho.assign(m,0.0);rho[r]=1.0;lu.btran(rho);
            compute_pivot_row(rho);
            const double sgn=delta<0?-1.0:1.0;
            cands.clear();
            for(int j:touched){
                if(status[j]==kBasic||lo[j]==up[j])continue;
                const double at=sgn*alpha_row[j];
                if(!(std::abs(at)>pivtol))continue;
                double dj;
                if(status[j]==kLower){if(at<=0)continue;dj=std::max(0.0,d[j]);}
                else if(status[j]==kUpper){if(at>=0)continue;dj=std::max(0.0,-d[j]);}
                else dj=0;
                const double a=std::abs(at);
                cands.push_back({j,dj/a,(dj+dt[j])/a,a});
            }
            int q=-1;flip_list.clear();
            if(!cands.empty()){
                std::sort(cands.begin(),cands.end(),[](const Candidate& a,const Candidate& b){return a.t<b.t||(a.t==b.t&&a.j<b.j);});
                hmin.assign(cands.size()+1,kInf);
                for(std::size_t k=cands.size();k-->0;)hmin[k]=std::min(hmin[k+1],cands[k].h);
                double slope=std::abs(delta);std::size_t at=0;
                const double slope_tolerance=to_lower?ptl[p]:ptu[p];
                while(at<cands.size()){
                    const double hmax=hmin[at];
                    std::size_t end=at;double sum=0;bool boxed=true;std::size_t chosen=at;double largest=-1;
                    while(end<cands.size()&&cands[end].t<=hmax){
                        const Candidate& cd=cands[end];const double range=up[cd.j]-lo[cd.j];
                        if(status[cd.j]==kFree||artificial[cd.j]||!std::isfinite(range))boxed=false;else sum+=cd.a*range;
                        if(cd.a>largest){largest=cd.a;chosen=end;}
                        ++end;
                    }
                    if(boxed&&slope-sum>slope_tolerance){
                        for(std::size_t k=at;k<end;++k)flip_list.push_back(cands[k].j);
                        slope-=sum;at=end;continue;
                    }
                    q=cands[chosen].j;break;
                }
            }
            if(q<0){
                // A (near) zero tableau row cannot remove a rounding-sized violation.
                // Skip it until the basis changes; final checks use the original model.
                // A verified ray ends the solve; otherwise a rounding-sized violation
                // whose row maximum sits exactly at the bound is degenerate noise.
                farkas=rho;
                if(!any_artificial&&verify_farkas(farkas,lower,upper))return "dual_unbounded";
                if(std::abs(delta)<=1e-6*(1+std::abs(target))){
                    ignored[r]=ignore_stamp;++ignored_count;continue;
                }
                return "dual_unbounded";
            }
            alpha.assign(m,0.0);
            for_column(q,[&](int i,double a){alpha[i]+=a;});
            lu.ftran(alpha);
            const double arq=alpha[r];
            const double arow=alpha_row[q];
            if(!(std::abs(arq-arow)<=1e-7*(1+std::abs(arq)))||!(std::abs(arq)>1e-11)){
                if(lu.etas()>0){if(!reinvert())return "numerical_error";continue;}
                return "numerical_error";
            }
            tau=rho;lu.ftran(tau);
            long double wr_long=0;for(double v:rho)wr_long+=static_cast<long double>(v)*v;
            const double wr=static_cast<double>(wr_long);
            double theta_d=0;
            const bool right_sign=status[q]==kLower?d[q]>=0:(status[q]==kUpper?d[q]<=0:false);
            if(right_sign)theta_d=d[q]/arq;
            else if(d[q]!=0){c[q]-=d[q];shifted=true;}
            if(theta_d!=0)for(int j:touched)if(status[j]!=kBasic)d[j]-=theta_d*alpha_row[j];
            d[q]=0;d[p]=-theta_d;
            // Harris steps can leave bounded, tolerance-sized wrong signs; shift them away.
            for(int j:touched){
                if(status[j]==kBasic||j==q||lo[j]==up[j])continue;
                if(status[j]==kLower&&d[j]<0){c[j]-=d[j];d[j]=0;shifted=true;}
                else if(status[j]==kUpper&&d[j]>0){c[j]-=d[j];d[j]=0;shifted=true;}
            }
            if(!flip_list.empty()){
                shift_rhs.assign(m,0.0);
                for(int j:flip_list){
                    // Flipped variables were passed by the dual step, so their new
                    // reduced-cost sign matches the opposite bound.
                    const double value=status[j]==kLower?up[j]:lo[j];const double dx=value-x[j];
                    x[j]=value;status[j]=status[j]==kLower?kUpper:kLower;
                    for_column(j,[&](int i,double a){shift_rhs[i]-=a*dx;});
                    if(status[j]==kLower&&d[j]<0){c[j]-=d[j];d[j]=0;shifted=true;}
                    else if(status[j]==kUpper&&d[j]>0){c[j]-=d[j];d[j]=0;shifted=true;}
                }
                lu.ftran(shift_rhs);
                for(int pos=0;pos<m;++pos)x[basic[pos]]+=shift_rhs[pos];
                stats.flips+=flip_list.size();
                delta=x[p]-target;
            }
            const double theta_p=delta/arq;
            for(int pos=0;pos<m;++pos)if(alpha[pos]!=0)x[basic[pos]]-=theta_p*alpha[pos];
            x[q]+=theta_p;x[p]=target;
            for(int pos=0;pos<m;++pos){
                if(pos==r)continue;
                const double a=alpha[pos];if(a==0)continue;
                const double ratio=a/arq;
                const double w=dse[pos]+ratio*(ratio*wr-2*tau[pos]);
                dse[pos]=std::max(w,std::max(ratio*ratio,1e-8));
            }
            dse[r]=std::max(wr/(arq*arq),1e-8);
            basic[r]=q;status[q]=kBasic;
            status[p]=(to_lower||lo[p]==up[p])?kLower:kUpper;
            lu.update(r,alpha);
            ++iterations;++stats.dual_iterations;
            if(std::isfinite(cutoff)){
                const double z=M.cost_scale*scaled_objective()+M.offset;
                if(z>=cutoff&&z>next_cutoff_check){
                    std::vector<double> y;current_duals(y);
                    const double b=safe_bound(y,lower,upper);
                    if(b>=cutoff){cutoff_bound=b;return "cutoff";}
                    next_cutoff_check=z+1e-9*(1+std::abs(z));
                }
            }
            if(lu.etas()>=64||lu.eta_nonzeros>4*lu.factor_nonzeros+8*static_cast<std::size_t>(m)){
                if(!reinvert())return "numerical_error";
            }
        }
    }

    // Primal phase from a primal feasible basis: Devex pricing, Harris ratio test.
    std::string primal_phase() {
        std::vector<double> devex(N,1.0);
        for(;;){
            if(expired())return "time_limit";
            if(iterations>=opt.iteration_limit)return "iteration_limit";
            int q=-1,dir=0;double best=0;
            for(int j=0;j<N;++j){
                if(status[j]==kBasic||lo[j]==up[j])continue;
                const double dj=d[j];double infeasibility=0;int dd=0;
                if(status[j]==kLower){if(dj<-dt[j]){infeasibility=-dj;dd=1;}}
                else if(status[j]==kUpper){if(dj>dt[j]){infeasibility=dj;dd=-1;}}
                else if(dj<-dt[j]&&x[j]<up[j]){infeasibility=-dj;dd=1;}
                else if(dj>dt[j]&&x[j]>lo[j]){infeasibility=dj;dd=-1;}
                if(dd){const double s=infeasibility*infeasibility/devex[j];if(s>best){best=s;q=j;dir=dd;}}
            }
            if(q<0)return "optimal";
            alpha.assign(m,0.0);
            for_column(q,[&](int i,double a){alpha[i]+=a;});
            lu.ftran(alpha);
            double hmax=kInf;
            for(int pos=0;pos<m;++pos){
                const double a=dir*alpha[pos];if(!(std::abs(a)>pivtol))continue;
                const int j=basic[pos];
                if(a>0){if(std::isfinite(lo[j]))hmax=std::min(hmax,(x[j]-lo[j]+ptl[j])/a);}
                else if(std::isfinite(up[j]))hmax=std::min(hmax,(up[j]-x[j]+ptu[j])/(-a));
            }
            const double own=dir>0?up[q]-x[q]:x[q]-lo[q];
            if(std::isfinite(own)&&own<=hmax){
                const double theta=std::max(0.0,own);
                for(int pos=0;pos<m;++pos)if(alpha[pos]!=0)x[basic[pos]]-=dir*theta*alpha[pos];
                status[q]=dir>0?kUpper:kLower;x[q]=dir>0?up[q]:lo[q];
                ++stats.flips;++iterations;++stats.primal_iterations;
                continue;
            }
            if(!std::isfinite(hmax))return "unbounded";
            int r=-1;double largest=0,theta=0;
            for(int pos=0;pos<m;++pos){
                const double a=dir*alpha[pos];if(!(std::abs(a)>pivtol))continue;
                const int j=basic[pos];double ratio;
                if(a>0){if(!std::isfinite(lo[j]))continue;ratio=(x[j]-lo[j])/a;}
                else {if(!std::isfinite(up[j]))continue;ratio=(up[j]-x[j])/(-a);}
                if(ratio<=hmax&&std::abs(a)>largest){largest=std::abs(a);r=pos;theta=ratio;}
            }
            if(r<0)return "numerical_error";
            theta=std::max(0.0,theta);
            const int p=basic[r];
            const bool to_lower=dir*alpha[r]>0;
            const double target=to_lower?lo[p]:up[p];
            const double arq=alpha[r];
            rho.assign(m,0.0);rho[r]=1.0;lu.btran(rho);
            compute_pivot_row(rho);
            const double arow=q>=0?(mark[q]==markv?alpha_row[q]:0.0):0.0;
            if(!(std::abs(arq-arow)<=1e-7*(1+std::abs(arq)))){
                if(lu.etas()>0){if(!refactor())return "numerical_error";compute_primal();compute_dual();continue;}
                return "numerical_error";
            }
            for(int pos=0;pos<m;++pos)if(alpha[pos]!=0)x[basic[pos]]-=dir*theta*alpha[pos];
            x[q]+=dir*theta;x[p]=target;
            const double theta_d=d[q]/arq;
            for(int j:touched)if(status[j]!=kBasic)d[j]-=theta_d*alpha_row[j];
            d[p]=-theta_d;d[q]=0;
            const double wq=devex[q];
            for(int j:touched){
                if(status[j]==kBasic||j==q)continue;
                const double ratio=alpha_row[j]/arq;
                devex[j]=std::max(devex[j],ratio*ratio*wq);
            }
            devex[p]=std::max(wq/(arq*arq),1.0);
            basic[r]=q;status[q]=kBasic;
            status[p]=(to_lower||lo[p]==up[p])?kLower:kUpper;
            lu.update(r,alpha);
            ++iterations;++stats.primal_iterations;
            if(lu.etas()>=64||lu.eta_nonzeros>4*lu.factor_nonzeros+8*static_cast<std::size_t>(m)){
                if(!refactor())return "numerical_error";
                compute_primal();compute_dual();
            }
        }
    }
    double max_primal_infeasibility()const {
        double worst=0;
        for(int pos=0;pos<m;++pos){
            const int j=basic[pos];
            if(x[j]<lo[j]-ptl[j])worst=std::max(worst,lo[j]-x[j]);
            if(x[j]>up[j]+ptu[j])worst=std::max(worst,x[j]-up[j]);
        }
        return worst;
    }
    // Remove cost shifts and artificial bounds, then restore optimality.
    std::string cleanup() {
        bool changed=false;
        if(shifted){c=c0;shifted=false;changed=true;}
        if(any_artificial){
            for(int j=0;j<N;++j){
                if(!artificial[j])continue;
                lo[j]=tlo[j];up[j]=tup[j];artificial[j]=0;
                if(status[j]==kLower&&!std::isfinite(lo[j]))status[j]=kFree;
                if(status[j]==kUpper&&!std::isfinite(up[j]))status[j]=kFree;
            }
            any_artificial=false;changed=true;
        }
        if(!changed)return "optimal";
        ++stats.cleanups;
        compute_dual();
        return primal_phase();
    }
    std::string run(double cutoff,const std::vector<double>& lower,const std::vector<double>& upper) {
        if(!refactor())return "numerical_error";
        compute_primal();compute_dual();make_dual_feasible();
        for(int round=0;round<4;++round){
            std::string s=dual_phase(cutoff,lower,upper);
            // Rounding-sized violations on zero tableau rows are left to the
            // original-model verification below.
            if(s=="ignored_rows")s="optimal";
            if(s!="optimal")return s;
            s=cleanup();
            if(s!="optimal")return s;
            if(!refactor())return "numerical_error";
            compute_primal();compute_dual();
            bool dual_ok=true;
            for(int j=0;j<N&&dual_ok;++j)dual_ok=dual_feasible(j);
            if(dual_ok&&max_primal_infeasibility()<=1e-7)return "optimal";
            if(expired())return "time_limit";
            make_dual_feasible();
        }
        return "numerical_error";
    }
};
}

std::shared_ptr<const BoundedLpModel> prepare_bounded_lp(const LinearProblem& p,bool scaling) {
    validate_linear_problem(p);
    auto out=std::make_shared<BoundedLpModel>();auto& M=*out;
    const std::size_t n=p.cost.size(),m=p.rows.size();
    if(n>=static_cast<std::size_t>(std::numeric_limits<int>::max()/2)||m>=static_cast<std::size_t>(std::numeric_limits<int>::max()/2))
        throw std::runtime_error("resource_limit: bounded LP dimensions");
    M.n=n;M.m=m;M.sense=p.maximize?-1:1;M.offset=M.sense*p.offset;
    M.row_start.assign(m+1,0);
    std::vector<std::pair<std::size_t,double> > entries;
    for(std::size_t i=0;i<m;++i){
        entries.assign(p.rows[i].begin(),p.rows[i].end());
        std::sort(entries.begin(),entries.end(),[](const std::pair<std::size_t,double>& a,const std::pair<std::size_t,double>& b){return a.first<b.first;});
        for(std::size_t k=0;k<entries.size();){
            std::size_t j=entries[k].first;long double sum=0;
            while(k<entries.size()&&entries[k].first==j)sum+=entries[k++].second;
            if(sum!=0){M.row_index.push_back(static_cast<int>(j));M.row_value.push_back(static_cast<double>(sum));}
        }
        if(M.row_value.size()>=static_cast<std::size_t>(std::numeric_limits<int>::max()/2))throw std::runtime_error("resource_limit: bounded LP nonzeros");
        M.row_start[i+1]=static_cast<int>(M.row_value.size());
    }
    M.row_scale.assign(m,1.0);M.col_scale.assign(n,1.0);
    if(scaling){
        std::vector<double> rs(m,1.0),cs(n,1.0);
        for(int pass=0;pass<6;++pass){
            std::vector<double> big(n,0.0),small(n,kInf);
            for(std::size_t i=0;i<m;++i){
                double hi=0,lo=kInf;
                for(int k=M.row_start[i];k<M.row_start[i+1];++k){double a=std::abs(M.row_value[k])*cs[M.row_index[k]];hi=std::max(hi,a);lo=std::min(lo,a);}
                if(hi>0)rs[i]=1/std::sqrt(hi*lo);
            }
            for(std::size_t i=0;i<m;++i)for(int k=M.row_start[i];k<M.row_start[i+1];++k){
                const int j=M.row_index[k];const double a=std::abs(M.row_value[k])*rs[i];
                big[j]=std::max(big[j],a);small[j]=std::min(small[j],a);
            }
            for(std::size_t j=0;j<n;++j)if(big[j]>0)cs[j]=1/std::sqrt(big[j]*small[j]);
        }
        auto power=[](double v){if(!(v>0)||!std::isfinite(v))return 1.0;int e=static_cast<int>(std::lround(std::log2(v)));e=std::max(-30,std::min(30,e));return std::ldexp(1.0,e);};
        for(std::size_t i=0;i<m;++i)M.row_scale[i]=power(rs[i]);
        for(std::size_t j=0;j<n;++j)M.col_scale[j]=power(cs[j]);
    }
    for(std::size_t i=0;i<m;++i)for(int k=M.row_start[i];k<M.row_start[i+1];++k)
        M.row_value[k]*=M.row_scale[i]*M.col_scale[M.row_index[k]];
    M.col_start.assign(n+1,0);
    for(int j:M.row_index)++M.col_start[j+1];
    for(std::size_t j=0;j<n;++j)M.col_start[j+1]+=M.col_start[j];
    M.col_index.resize(M.row_index.size());M.col_value.resize(M.row_value.size());
    std::vector<int> fill(M.col_start.begin(),M.col_start.end()-1);
    for(std::size_t i=0;i<m;++i)for(int k=M.row_start[i];k<M.row_start[i+1];++k){
        const int at=fill[M.row_index[k]]++;M.col_index[at]=static_cast<int>(i);M.col_value[at]=M.row_value[k];
    }
    M.cost.resize(n);double largest=0;
    for(std::size_t j=0;j<n;++j){M.cost[j]=M.sense*p.cost[j]*M.col_scale[j];largest=std::max(largest,std::abs(M.cost[j]));}
    if(scaling&&largest>1){int e=static_cast<int>(std::lround(std::log2(largest)));M.cost_scale=std::ldexp(1.0,std::min(60,e));}
    for(double& v:M.cost)v/=M.cost_scale;
    return out;
}

SparseLpResult solve_bounded_lp(const LinearProblem& p,const BoundedLpModel& M,
        const std::vector<double>& lower,const std::vector<double>& upper,const Options& opt,
        const BoundedBasis* warm,double cutoff,BoundedLpStats* stats_out) {
    const auto started=std::chrono::steady_clock::now();
    BoundedLpStats stats;++stats.calls;
    SparseLpResult out;auto& r=out.solution;
    const std::size_t n=M.n,m=M.m;
    if(p.cost.size()!=n||p.rows.size()!=m||lower.size()!=n||upper.size()!=n)throw std::invalid_argument("Bounded LP model mismatch");
    if(!std::isfinite(opt.tolerance)||opt.tolerance<=0||!std::isfinite(opt.time_limit_seconds)||opt.time_limit_seconds<0)
        throw std::invalid_argument("Invalid LP options");
    auto finish=[&](){
        stats.seconds+=std::chrono::duration<double>(std::chrono::steady_clock::now()-started).count();
        if(stats_out)stats_out->add(stats);
        return out;
    };
    for(std::size_t j=0;j<n;++j)if(std::isnan(lower[j])||std::isnan(upper[j])||lower[j]==kInf||upper[j]==-kInf)throw std::invalid_argument("Invalid bounded LP bounds");
    for(std::size_t j=0;j<n;++j)if(lower[j]>upper[j]){r.status="infeasible";r.infeasibility_verified=true;++stats.infeasible;return finish();}
    for(std::size_t i=0;i<m;++i)if(p.row_lower[i]>p.row_upper[i]){r.status="infeasible";r.infeasibility_verified=true;++stats.infeasible;return finish();}
    std::unique_ptr<Engine> engine(new Engine(p,M,opt,stats));
    engine->began=started;
    engine->setup(lower,upper);
    bool warmed=warm&&engine->warm_start(*warm);
    if(!warmed){engine->setup(lower,upper);engine->cold_start();++stats.cold;}else ++stats.warm;
    std::string status=engine->run(cutoff,lower,upper);
    std::size_t iterations=engine->iterations;
    if(warmed&&(status=="numerical_error"||(status=="dual_unbounded"&&!engine->verify_farkas(engine->farkas,lower,upper)))&&!engine->expired()) {
        // A reused basis can be numerically poor; retry once from the slack basis.
        engine.reset(new Engine(p,M,opt,stats));
        engine->began=started;engine->setup(lower,upper);engine->cold_start();++stats.cold;warmed=false;
        status=engine->run(cutoff,lower,upper);
        engine->iterations+=iterations;
    }
    Engine& e=*engine;
    out.warm_started=warmed;
    stats.iterations+=e.iterations;
    r.iterations=e.iterations;
    out.factorizations=stats.refactors;
    auto basis=std::make_shared<BoundedBasis>();
    basis->structural=n;basis->status=e.status;
    if(status=="dual_unbounded"){
        if(e.verify_farkas(e.farkas,lower,upper)){
            r.status="infeasible";r.infeasibility_verified=true;++stats.infeasible;
            out.basis.bounded=basis;
        } else {
            if(std::getenv("SOVEREIGN_BOUNDED_DEBUG"))std::fprintf(stderr,"bounded farkas rejected warm=%d artificial=%d it=%zu\n",int(warmed),int(e.any_artificial),e.iterations);
            r.status="numerical_error";++stats.farkas_rejected;++stats.failures;
        }
        return finish();
    }
    if(status=="cutoff"){
        r.status="cutoff";out.best_bound=e.cutoff_bound;out.basis.bounded=basis;++stats.cutoffs;
        return finish();
    }
    if(status!="optimal"){
        if(std::getenv("SOVEREIGN_BOUNDED_DEBUG"))std::fprintf(stderr,"bounded failure status=%s warm=%d it=%zu\n",status.c_str(),int(warmed),e.iterations);
        r.status=status;++stats.failures;return finish();
    }
    // Original-space solution and independent checks (same contract as solve_sparse_lp).
    r.primal.assign(n,0.0);
    for(std::size_t j=0;j<n;++j)r.primal[j]=e.x[j]*M.col_scale[j];
    for(std::size_t j=0;j<n;++j){
        // Snap values within scaled tolerance of a finite bound to that bound.
        if(e.status[j]==kLower&&std::isfinite(lower[j]))r.primal[j]=lower[j];
        else if(e.status[j]==kUpper&&std::isfinite(upper[j]))r.primal[j]=upper[j];
    }
    long double objective=p.offset;
    for(std::size_t j=0;j<n;++j)objective+=static_cast<long double>(p.cost[j])*r.primal[j];
    r.objective=static_cast<double>(objective);
    double absolute=0,scaled=0;
    auto check=[&](long double activity,double bound,bool lower_side,long double magnitude){
        if(!std::isfinite(bound))return;
        long double v=lower_side?bound-activity:activity-bound;
        absolute=std::max(absolute,static_cast<double>(v));
        scaled=std::max(scaled,static_cast<double>(v/(1+std::abs(bound)+magnitude)));
    };
    for(std::size_t j=0;j<n;++j){
        if(!std::isfinite(r.primal[j])){absolute=scaled=kInf;break;}
        check(r.primal[j],lower[j],true,std::abs(r.primal[j]));check(r.primal[j],upper[j],false,std::abs(r.primal[j]));
    }
    std::vector<long double> activities(m,0);
    for(std::size_t i=0;i<m&&std::isfinite(absolute);++i){
        long double activity=0,magnitude=0;
        for(auto a:p.rows[i]){long double t=static_cast<long double>(a.second)*r.primal[a.first];activity+=t;magnitude+=std::abs(t);}
        activities[i]=activity;
        check(activity,p.row_lower[i],true,magnitude);check(activity,p.row_upper[i],false,magnitude);
    }
    r.max_violation=absolute;r.scaled_primal_violation=scaled;
    std::vector<double> y;e.current_duals(y);
    std::vector<long double> yo(m),dj(n),mag(n);
    for(std::size_t i=0;i<m;++i)yo[i]=static_cast<long double>(y[i])*M.row_scale[i]*M.cost_scale;
    for(std::size_t j=0;j<n;++j){dj[j]=M.sense*p.cost[j];mag[j]=1+std::abs(p.cost[j]);}
    // Complementarity form of the dual objective: a multiplier whose required
    // row side is infinite is a scaled dual violation and is priced at the activity.
    long double dual_objective=M.offset;
    double dual_violation=0;
    for(std::size_t i=0;i<m;++i){
        const long double v=yo[i];if(v==0)continue;
        for(auto a:p.rows[i]){long double t=v*a.second;dj[a.first]-=t;mag[a.first]+=std::abs(t);}
        const double side=v>0?p.row_lower[i]:p.row_upper[i];
        if(std::isfinite(side))dual_objective+=v*side;
        else {
            dual_violation=std::max(dual_violation,static_cast<double>(std::abs(v)/(1+std::abs(v))));
            dual_objective+=v*activities[i];
        }
    }
    for(std::size_t j=0;j<n;++j){
        long double v=dj[j];
        // Rounding-level reduced costs of interior columns are zero; otherwise a
        // remote finite bound (e.g. 1e12) turns noise into an apparent gap.
        if(std::abs(v)<=1e-13*mag[j]&&r.primal[j]>lower[j]&&r.primal[j]<upper[j])v=0;
        if(v==0)continue;
        const double side=v>0?lower[j]:upper[j];
        if(std::isfinite(side))dual_objective+=v*side;
        else {
            dual_violation=std::max(dual_violation,static_cast<double>(std::abs(v)/mag[j]));
            dual_objective+=v*r.primal[j];
        }
    }
    r.scaled_dual_violation=dual_violation;
    const long double primal_min=M.sense*objective;
    r.relative_gap=static_cast<double>(std::abs(primal_min-dual_objective)/(1+std::max(std::abs(primal_min),std::abs(dual_objective))));
    r.dual.assign(m,0.0);out.row_dual.assign(m,0.0);
    for(std::size_t i=0;i<m;++i){r.dual[i]=static_cast<double>(yo[i]);out.row_dual[i]=r.dual[i];}
    r.optimality_verified=std::isfinite(r.objective)&&scaled<=10*opt.tolerance&&dual_violation<=10*opt.tolerance&&r.relative_gap<=10*opt.tolerance;
    if(!r.optimality_verified){
        if(std::getenv("SOVEREIGN_BOUNDED_DEBUG")){
            std::fprintf(stderr,"bounded verification primal=%g dual=%g gap=%g abs=%g warm=%d it=%zu P=%.17g D=%.17g\n",scaled,dual_violation,r.relative_gap,absolute,int(warmed),e.iterations,double(primal_min),double(dual_objective));
            for(std::size_t j=0;j<n;++j){
                long double v=dj[j];if(std::abs(v)<=1e-13*mag[j]&&r.primal[j]>lower[j]&&r.primal[j]<upper[j])v=0;
                const double side=v>0?lower[j]:upper[j];
                const long double term=std::isfinite(side)?v*(r.primal[j]-side):0;
                if(std::abs(term)>1e-6)std::fprintf(stderr,"  col %zu d=%g x=%.17g lo=%g up=%g status=%d term=%g\n",j,double(v),r.primal[j],lower[j],upper[j],int(e.status[j]),double(term));
            }
            for(std::size_t i=0;i<m;++i){
                const long double v=yo[i];if(v==0)continue;
                const double side=v>0?p.row_lower[i]:p.row_upper[i];
                const long double term=std::isfinite(side)?v*(activities[i]-side):0;
                if(std::abs(term)>1e-6)std::fprintf(stderr,"  row %zu y=%g act=%.17g lo=%g up=%g status=%d term=%g\n",i,double(v),double(activities[i]),p.row_lower[i],p.row_upper[i],int(e.status[n+i]),double(term));
            }
        }
        r.status="numerical_error";++stats.verification_rejected;++stats.failures;return finish();
    }
    r.status="optimal";++stats.optimal;
    out.best_bound=e.safe_bound(y,lower,upper);
    if(!std::isfinite(out.best_bound))out.best_bound=static_cast<double>(dual_objective);
    out.basis.bounded=basis;
    return finish();
}

SparseLpResult solve_bounded_lp(const LinearProblem& p,const Options& opt,const BoundedBasis* warm,BoundedLpStats* stats) {
    auto model=prepare_bounded_lp(p,opt.scaling);
    if(stats)++stats->prepared;
    return solve_bounded_lp(p,*model,p.lower,p.upper,opt,warm,std::numeric_limits<double>::infinity(),stats);
}
}
