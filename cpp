/*
1. iostream include 
2. unique ptr <memory>
3. namespace / using namespace
4. class (public/private/protected/friend)
5. class init (variable/member function)
6. class operator overloading
7. pointer function
8. static_cast (provide validity of casting)
9. create heap space (new syntax)
10. template
11. static class function
12. pass by reference
13. include <cstdio> / <cstring> / <cstdlib> / <cstdint>
*/

#include <iostream>
#include <memory>

using namespace std;

namespace TF {
class Inter{
public:
    // member variable
    int m_a;
    // constructor
    Inter(void): m_a(4), m_b(5), m_c(6) { cout << "created m_a is " << m_a << endl; };
    // destructor
    ~Inter(void){ cout << "destroy m_a is " << m_a << endl; };
    // operator overloading
    void operator +=(const Inter& x);
    // template + static + auto
    template <class T> static T sq(const Inter& x){ auto a = (T)x.m_a; return a * a / 3.14;};
    // plass by reference
    static void zero(Inter& x) { x.m_a = 0;};
    // friend function -> able to access private/protected member variable  but the definition is outside class scope
    friend void print(const Inter& x);
private:
    // member variable can only be accessed by in class function
    int m_b;
protected:
    // member variable can be accessed by inherit class
    int m_c;
};

void print(const Inter& x) { cout << "print: c:" << x.m_c << endl; };
void TF::Inter::operator +=(const Inter& x)
{
    m_a = m_a + (int)x.m_a * 2;
    return;
}

} // TF

unique_ptr<TF::Inter> get_ptr(void)
{
    #if 0
    auto a = new Inter;
    a->m_a = 3;
    return unique_ptr<Inter>(a);
    #else
    return unique_ptr<TF::Inter>(new TF::Inter);
    #endif
}



void *app(void)
{
    //auto b = get_ptr();
    TF::Inter _a, _b;
    _b.m_a = 10;
    _a.m_a = 6;
    _a += _b;
    auto b = get_ptr();
    b->m_a = _a.m_a;
    cout <<  b.get() <<  " " << __func__ <<  " " << b->m_a << " sq:" << TF::Inter::sq<int>(*(b.get())) << endl;
    TF::Inter::zero(_a);
    cout << " a :" << _a.m_a << endl;
    print(_a);
    return b.get();
}

int main(void)
{
    auto c = app();
    cout << c << " " << (static_cast<TF::Inter*>(c))->m_a << endl;
    return 0;
}
