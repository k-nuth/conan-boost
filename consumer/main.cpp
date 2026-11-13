#include <boost/version.hpp>
#include <boost/unordered/unordered_flat_map.hpp>
#include <boost/unordered/unordered_flat_set.hpp>
#include <boost/unordered/concurrent_flat_map.hpp>
#include <boost/bloom/filter.hpp>
#include <boost/multiprecision/cpp_int.hpp>
#include <boost/smart_ptr/atomic_shared_ptr.hpp>
#include <boost/smart_ptr/make_shared.hpp>
#include <boost/bimap.hpp>
#include <cstdint>
#include <stdexcept>
#include <thread>
#include <vector>
#ifdef TEST_NATIVE
#include <boost/thread.hpp>
#endif

static_assert(BOOST_VERSION == EXPECTED_BOOST_VERSION);
void check(bool ok) { if (!ok) throw std::runtime_error("Boost consumer check failed"); }
struct snapshot { std::uint64_t value; std::uint64_t inverse; };
int main() {
    boost::unordered_flat_map<int, int> flat;
    flat.emplace(1, 42);
    check(flat.at(1) == 42);
    boost::unordered_flat_set<int> set{1, 2};
    check(set.contains(2));
    boost::bloom::filter<std::uint64_t, 7> bloom(4096);
    for (unsigned i=0;i<100;++i) bloom.insert(i);
    for (unsigned i=0;i<100;++i) check(bloom.may_contain(i));
    boost::multiprecision::uint256_t large = 1;
    large <<= 200;
    check((large >> 200) == 1);
    boost::bimap<int, int> both;
    both.insert({1, 2});
    check(both.right.at(2) == 1);
    boost::concurrent_flat_map<unsigned, unsigned> concurrent;
    boost::atomic_shared_ptr<snapshot const> published{
        boost::make_shared<snapshot const>(snapshot{0, ~std::uint64_t{0}})};
    std::vector<std::thread> workers;
    for (unsigned t=0;t<4;++t) workers.emplace_back([&,t] {
        for (unsigned i=0;i<500;++i) {
            auto const key=t*500+i;
            concurrent.emplace(key, key);
            published.store(boost::make_shared<snapshot const>(snapshot{key, ~std::uint64_t{key}}));
            auto const read=published.load();
            check(read->inverse == ~read->value);
        }
    });
    for (auto& worker:workers) worker.join();
    check(concurrent.size() == 2000);
#ifdef TEST_NATIVE
    boost::shared_mutex mutex;
    unsigned count=0;
    workers.clear();
    for (unsigned t=0;t<4;++t) workers.emplace_back([&] {
        for (unsigned i=0;i<500;++i) {boost::unique_lock lock(mutex);++count;}
    });
    for (auto& worker:workers) worker.join();
    boost::shared_lock lock(mutex);
    check(count == 2000);
#endif
}
