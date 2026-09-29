// Charged a=0 invariant sector of the original Signal Space Hamiltonian.
// Restart saved data; keep all fields inside |x|<T+150, taper only outside.
#include <vector>
#include <cmath>
#include <string>
#include <fstream>
#include <iostream>
#include <iomanip>
using namespace std;
int main(int argc,char**argv){
 if(argc<7){cerr<<"prefix input dx dt T sample_dt\n";return 1;}
 bool ledger_only=argc>7;string pre=argv[1];double h=stod(argv[3]),dt=stod(argv[4]),T=stod(argv[5]),sample=stod(argv[6]);int nt=lround(T/dt),stride=lround(sample/dt);dt=T/nt;
 double L=T+200;int N=2*lround(L/h)+1,mid=N/2;
 ifstream in(argv[2],ios::binary);int ni;double hi;in.read((char*)&ni,4);in.read((char*)&hi,8);vector<double> raw(4*ni);in.read((char*)raw.data(),raw.size()*8);if(!in)return 2;
 vector<double> u(N),z(N),v(N),y(N);
 auto interp=[&](int c,double x){double jj=x/hi+ni/2;int j=floor(jj);double f=jj-j;if(j<0||j+1>=ni)return 0.;return (1-f)*raw[c*ni+j]+f*raw[c*ni+j+1];};
 for(int j=1;j<N-1;j++){double x=(j-mid)*h,ax=abs(x),tap=ax<L-50?1.:.5*(1+cos(M_PI*(ax-L+50)/50));u[j]=interp(0,x)*tap;z[j]=interp(1,x)*tap;v[j]=interp(2,x)*tap;y[j]=interp(3,x)*tap;}
 ofstream field(ledger_only?"/dev/null":pre+"_field.bin",ios::binary),probes(ledger_only?"/dev/null":pre+"_probes.bin",ios::binary),ledger(pre+"_ledger.csv");ledger<<setprecision(16)<<"t,E,Q,E20,Q20,E40,Q40,E60,Q60\n";
 double hs=.05;int nx=1201;field.write((char*)&nx,4);field.write((char*)&hs,8);
 vector<double> places={-80,-60,-40,-30,-20,0,20,30,40,60,80};int np=places.size();probes.write((char*)&np,4);probes.write((char*)places.data(),np*8);
 for(int n=0;n<=nt;n++){
  if(!ledger_only && (n%stride==0 || n==nt)){double t=n*dt;double tf=t+.5*dt;field.write((char*)&tf,8);for(auto*ar:{&u,&z})for(int j=0;j<nx;j++){double xx=(j-nx/2)*hs;int ix=mid+lround(xx/h);double a=(*ar)[ix]+.5*dt*(ar==&u?v[ix]:y[ix]);field.write((char*)&a,8);}
   probes.write((char*)&t,8);for(double xx:places){int j=mid+lround(xx/h);double a[8]={u[j],z[j],v[j],y[j],(u[j+1]-u[j-1])/(2*h),(z[j+1]-z[j-1])/(2*h),u[j+1]-u[j],z[j+1]-z[j]};probes.write((char*)a,64);}
  }
  if(n%lround(1./dt)==0 || n==nt){double E=0,Q=0,ec[3]={},qc[3]={};for(int j=1;j<N-1;j++){double s=u[j]*u[j]+z[j]*z[j],ur=(u[j+1]-u[j])/h,zr=(z[j+1]-z[j])/h,ul=(u[j]-u[j-1])/h,zl=(z[j]-z[j-1])/h;
    double en=(v[j]*v[j]+y[j]*y[j]+.5*(ur*ur+zr*zr+ul*ul+zl*zl)+s-s*s+s*s*s)*h/.01,q=2*(z[j]*v[j]-u[j]*y[j])*h/.01;E+=en;Q+=q;double x=(j-mid)*h;for(int c=0;c<3;c++)if(abs(x)<=20*(c+1)+h/4){ec[c]+=en;qc[c]+=q;}}
   E+=(u[1]*u[1]+z[1]*z[1]+u[N-2]*u[N-2]+z[N-2]*z[N-2])/(2*h*.01);
   ledger<<n*dt<<","<<E<<","<<Q;for(int c=0;c<3;c++)ledger<<","<<ec[c]<<","<<qc[c];ledger<<"\n";
  }
  if(n==nt)break;
  for(int j=1;j<N-1;j++){u[j]+=.5*dt*v[j];z[j]+=.5*dt*y[j];}
  for(int j=1;j<N-1;j++){double s=u[j]*u[j]+z[j]*z[j],f=-1+2*s-3*s*s;v[j]+=dt*((u[j+1]-2*u[j]+u[j-1])/(h*h)+f*u[j]);y[j]+=dt*((z[j+1]-2*z[j]+z[j-1])/(h*h)+f*z[j]);}
  for(int j=1;j<N-1;j++){u[j]+=.5*dt*v[j];z[j]+=.5*dt*y[j];}
 }
 field.flush();probes.flush();ledger.flush();if(!field||!probes||!ledger)return 3;
}
