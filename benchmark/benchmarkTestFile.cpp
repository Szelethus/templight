template <int N>
struct fib
{
  static const int value = fib<N-1>::value + fib<N-2>::value;
};

template <>
struct fib<0>
{
  static const int value = 1;
};

template <>
struct fib<1>
{
  static const int value = 1;
};

fib<40> x;

template <long long N>
struct fact
{
  static const long long value = fact<N-1>::value * N; 
};

template <>
struct fact<1>
{
  static const long long value = 1;
};

fact<20> y;
