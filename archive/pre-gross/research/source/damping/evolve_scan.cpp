// Same drift-kick-drift charged-sector update as supplied milestone.
// Even initial data are evolved on x>=0 with reflection at x=0.
#include <vector>
#include <cmath>
#include <string>
#include <fstream>
#include <iostream>
#include <iomanip>
using namespace std;
int main(int argc,char**argv){
 if(argc<7)return 1;
 string pre=argv[1];double h=stod(argv[3]),dt=stod(argv[4]),T=stod(argv[5]),sample=stod(argv[6]);int nt=lround(T/dt),stride=lround(sample/dt);dt=T/nt;
 double L=T+120;int N=lround(L/h)+1;
 ifstream in(argv[2],ios::binary);int ni;double hi;in.read((char*)&ni,4);in.read((char*)&hi,8);vector<double>raw(4*ni);in.read((char*)raw.data(),raw.size()*8);if(!in)return 2;
 vector<double>u(N),z(N),v(N),y(N);
 for(int j=0;j<N;j++){int jj=ni/2+lround(j*h/hi);if(jj<ni){u[j]=raw[jj];z[j]=raw[ni+jj];v[j]=raw[2*ni+jj];y[j]=raw[3*ni+jj];}}
 ofstream probes(pre+"_probes.bin",ios::binary),ledger(pre+"_ledger.csv");ledger<<setprecision(16)<<"t,E,Q,E20,Q20,E40,Q40,E60,Q60,intP20,intJ20\n";
 vector<double>places={0,.5,1,2,3,5,10,20,30,40,60};int np=places.size();probes.write((char*)&np,4);probes.write((char*)places.data(),np*8);
 int jd=lround(20/h);double Ip=0,Iq=0;
 auto flux=[&](){double du=u[jd+1]-u[jd],dz=z[jd+1]-z[jd];double P=-2*((v[jd]+v[jd+1])*du+(y[jd]+y[jd+1])*dz)/(.01*h),J=4*(u[jd]*z[jd+1]-z[jd]*u[jd+1])/(.01*h);return pair<double,double>(P,J);};
 for(int n=0;n<=nt;n++){
  if(n%stride==0 || n==nt){double t=n*dt;probes.write((char*)&t,8);for(double xx:places){int j=lround(xx/h);double a[8]={u[j],z[j],v[j],y[j],j?(u[j+1]-u[j-1])/(2*h):0,j?(z[j+1]-z[j-1])/(2*h):0,u[j+1]-u[j],z[j+1]-z[j]};probes.write((char*)a,64);}}
  if(n%lround(1./dt)==0 || n==nt){double E=0,Q=0,ec[3]={},qc[3]={};for(int j=0;j<N-1;j++){double s=u[j]*u[j]+z[j]*z[j],ur=(u[j+1]-u[j])/h,zr=(z[j+1]-z[j])/h,ul=j?(u[j]-u[j-1])/h:ur,zl=j?(z[j]-z[j-1])/h:zr;
    double fac=j?2:1;double en=fac*(v[j]*v[j]+y[j]*y[j]+.5*(ur*ur+zr*zr+ul*ul+zl*zl)+s-s*s+s*s*s)*h/.01,q=fac*2*(z[j]*v[j]-u[j]*y[j])*h/.01;E+=en;Q+=q;double x=j*h;for(int c=0;c<3;c++)if(x<=20*(c+1)+h/4){ec[c]+=en;qc[c]+=q;}}
   E+=(u[N-2]*u[N-2]+z[N-2]*z[N-2])/(h*.01);
   ledger<<n*dt<<","<<E<<","<<Q;for(int c=0;c<3;c++)ledger<<","<<ec[c]<<","<<qc[c];ledger<<","<<Ip<<","<<Iq<<"\n";
  }
  if(n==nt)break;auto before=flux();
  for(int j=0;j<N-1;j++){u[j]+=.5*dt*v[j];z[j]+=.5*dt*y[j];}
  for(int j=0;j<N-1;j++){double s=u[j]*u[j]+z[j]*z[j],f=-1+2*s-3*s*s;double lu=j?(u[j+1]-2*u[j]+u[j-1]):2*(u[1]-u[0]);double lz=j?(z[j+1]-2*z[j]+z[j-1]):2*(z[1]-z[0]);v[j]+=dt*(lu/(h*h)+f*u[j]);y[j]+=dt*(lz/(h*h)+f*z[j]);}
  for(int j=0;j<N-1;j++){u[j]+=.5*dt*v[j];z[j]+=.5*dt*y[j];}
  auto after=flux();Ip+=.5*dt*(before.first+after.first);Iq+=.5*dt*(before.second+after.second);
 }
 return (!probes||!ledger)?3:0;
}
