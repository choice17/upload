/*
https://www.w3schools.com/cpp/
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
14. unnamed scope resolution
15. runtime polymorphism
16. class static variable
17. delete[] operator for heap array
*/

#include <iostream>
#include <memory>

using namespace std;

namespace TF {
class Base{
public:
    Base(){};
    ~Base(){};
    virtual void echo(void){ cout << "I am from base class!" << endl; }
};

class Inter: public Base{
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
    
    void echo(void){cout << "I am from Inter class\n";}
    
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

int g_x = 3;

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
    TF::Base _base;
    TF::Base* _bptr;
    TF::Inter _a, _b;
    _b.m_a = 10;
    _a.m_a = 6;
    _a += _b;
    
    // test for runtime polymorphism
    _bptr = &_base;
    _bptr->echo();
    _bptr = &_a;
    _bptr->echo();
    auto b = get_ptr();
    b->m_a = _a.m_a;
    cout <<  b.get() <<  " " << __func__ <<  " " << b->m_a << " sq:" << TF::Inter::sq<int>(*(b.get())) << endl;
    TF::Inter::zero(_a);
    cout << " a :" << _a.m_a << endl;
    print(_a);
    return b.get();
}

class TEST
{
public:
    static int cnt;
    TEST(){cnt++; x = cnt;}
    ~TEST(){cout << "delete " << x << endl;}
    int x;
};

int TEST::cnt = 0; // must init outside class definition

int main(void)
{
    auto c = app();
    int g_x = 4; //local scope 
    cout << c << " " << (static_cast<TF::Inter*>(c))->m_a << endl;
    cout << ::g_x << " global vs local " << g_x << endl;
    
    TEST *t = new TEST[10];
    delete[] t; // array delete operator
    return 0;
}
