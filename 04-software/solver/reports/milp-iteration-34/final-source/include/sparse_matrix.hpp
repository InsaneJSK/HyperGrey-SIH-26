#pragma once
#include "sparse_lu.hpp"

namespace sovereign {
struct CsrMatrix {
    std::size_t rows=0,cols=0;
    std::vector<int> start,index;
    std::vector<double> value;
    CsrMatrix()=default;
    CsrMatrix(std::size_t columns,const std::vector<SparseVector>& input):rows(input.size()),cols(columns),start(input.size()+1,0) {
        for(std::size_t i=0;i<rows;++i) {
            std::map<std::size_t,double> merged;for(auto a:input[i])merged[a.first]+=a.second;
            for(auto a:merged)if(a.second!=0){index.push_back(static_cast<int>(a.first));value.push_back(a.second);}
            if(value.size()>2000000000)throw std::runtime_error("Sparse matrix index budget exceeded");
            start[i+1]=static_cast<int>(value.size());
        }
    }
    CsrMatrix transpose() const {
        CsrMatrix t;t.rows=cols;t.cols=rows;t.start.assign(cols+1,0);t.index.resize(value.size());t.value.resize(value.size());
        for(auto j:index)++t.start[j+1];
        for(std::size_t j=0;j<cols;++j)t.start[j+1]+=t.start[j];
        auto position=t.start;
        for(std::size_t i=0;i<rows;++i)for(int k=start[i];k<start[i+1];++k){int at=position[index[k]]++;t.index[at]=static_cast<int>(i);t.value[at]=value[k];}
        return t;
    }
    void multiply(const std::vector<double>& x,std::vector<double>& y,int threads=1) const {
        y.resize(rows);
        #ifdef _OPENMP
        #pragma omp parallel for num_threads(threads) if(threads>1 && rows>2000) schedule(static)
        #endif
        for(long long i=0;i<static_cast<long long>(rows);++i){double sum=0;for(int k=start[i];k<start[i+1];++k)sum+=value[k]*x[index[k]];y[i]=sum;}
        (void)threads;
    }
};
}
