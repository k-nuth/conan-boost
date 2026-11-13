#include <boost/stacktrace.hpp>
int main() {
    boost::stacktrace::stacktrace trace;
    return trace.empty() ? 1 : 0;
}
