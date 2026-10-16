#include "accelerated_qp.hpp"
#include <cuda_runtime.h>
#include <stdexcept>

namespace sovereign {
namespace {
void checked(cudaError_t e){if(e!=cudaSuccess)throw std::runtime_error(std::string("CUDA: ")+cudaGetErrorString(e));}
template<class T> struct DeviceArray {
    T* data=nullptr;std::size_t size;
    explicit DeviceArray(const std::vector<T>& source):size(source.size()) {
        if(size){checked(cudaMalloc(reinterpret_cast<void**>(&data),size*sizeof(T)));try{checked(cudaMemcpy(data,source.data(),size*sizeof(T),cudaMemcpyHostToDevice));}catch(...){cudaFree(data);data=nullptr;throw;}}
    }
    ~DeviceArray(){if(data)cudaFree(data);}
    DeviceArray(const DeviceArray&)=delete;DeviceArray& operator=(const DeviceArray&)=delete;
};
__global__ void csr_product(int n,const int* start,const int* column,const double* value,const double* x,double* y) {
    int i=blockIdx.x*blockDim.x+threadIdx.x;if(i<n){double sum=0;for(int k=start[i];k<start[i+1];++k)sum+=value[k]*x[column[k]];y[i]=sum;}
}
__global__ void fista_step(int n,double* x,double* w,const double* hx,const double* c,const double* lower,const double* upper,double step,double beta) {
    int j=blockIdx.x*blockDim.x+threadIdx.x;if(j<n){double next=fmax(lower[j],fmin(upper[j],w[j]-step*(hx[j]+c[j])));w[j]=next+beta*(next-x[j]);x[j]=next;}
}
struct CudaBox:BoxIteration {
    int n;double stepsize;
    DeviceArray<int> start,column;
    DeviceArray<double> value,c,lower,upper,x,w,gradient;
    static std::vector<double> initial(const std::vector<double>& lo,const std::vector<double>& up){std::vector<double> x(lo.size());for(std::size_t j=0;j<x.size();++j)x[j]=std::max(lo[j],std::min(up[j],0.0));return x;}
    CudaBox(const CsrMatrix& h,const std::vector<double>& cost,const std::vector<double>& lo,const std::vector<double>& up,double l):
        n(static_cast<int>(cost.size())),stepsize(1/l),start(h.start),column(h.index),value(h.value),c(cost),lower(lo),upper(up),x(initial(lo,up)),w(initial(lo,up)),gradient(std::vector<double>(lo.size())){}
    void step_impl(double beta){csr_product<<<(n+255)/256,256>>>(n,start.data,column.data,value.data,w.data,gradient.data);checked(cudaGetLastError());fista_step<<<(n+255)/256,256>>>(n,x.data,w.data,gradient.data,c.data,lower.data,upper.data,stepsize,beta);checked(cudaGetLastError());}
    void step(double beta) override {step_impl(beta);}
    std::vector<double> primal() override {std::vector<double> out(n);checked(cudaMemcpy(out.data(),x.data,n*sizeof(double),cudaMemcpyDeviceToHost));return out;}
};
}
std::unique_ptr<BoxIteration> make_cuda_box(const CsrMatrix& h,const std::vector<double>& c,const std::vector<double>& lo,const std::vector<double>& up,double l) {
    int devices=0;checked(cudaGetDeviceCount(&devices));if(!devices)throw std::runtime_error("No CUDA device available");
    return std::unique_ptr<BoxIteration>(new CudaBox(h,c,lo,up,l));
}
std::string cuda_device_name(){int count=0;checked(cudaGetDeviceCount(&count));if(!count)return "No CUDA device available";cudaDeviceProp p;checked(cudaGetDeviceProperties(&p,0));return p.name;}
}
