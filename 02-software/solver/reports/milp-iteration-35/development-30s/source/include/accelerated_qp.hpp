#pragma once
#include "qp.hpp"
#include "sparse_matrix.hpp"
#include <memory>

namespace sovereign {
// Resident-device first-order engine for continuous, convex box QPs.
// General linear constraints remain on the independently tested CPU QP path.
struct BoxIteration {
    virtual ~BoxIteration() {}
    virtual void step(double momentum)=0;
    virtual std::vector<double> primal()=0;
};
std::unique_ptr<BoxIteration> make_cuda_box(const CsrMatrix&,const std::vector<double>& cost,
    const std::vector<double>& lower,const std::vector<double>& upper,double lipschitz);
std::string cuda_device_name();
QpResult solve_accelerated_box(const QuadraticProblem&,const QpOptions&,bool cuda);
}
