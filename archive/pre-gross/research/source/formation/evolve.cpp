// Signal Space formation: local Hamiltonian A/2 B/2 C B/2 A/2 integrator.
// Variables Re Phi, Im Phi, their velocities, a, b=Z*a_t; lambda=0.01.
#include <cmath>
#include <vector>
#include <fstream>
#include <iostream>
#include <iomanip>
#include <string>
#include <algorithm>
using namespace std;
int main(int argc,char**argv){
 if(argc<10){cerr<<"evolve prefix omega width_ratio nu dx dt T mode neutral_fraction [input.bin] [phase] [separation]\n";return 1;}
 string out=argv[1],mode=argv[8]; double om=stod(argv[2]),wr=stod(argv[3]),nu=stod(argv[4]),dx=stod(argv[5]),dt=stod(argv[6]),T=stod(argv[7]),frac=stod(argv[9]);
 const double lam=.01,eps=.1; double kap=sqrt(1-om*om),d=sqrt(1-4*kap*kap),I=atanh(2*kap),Q=2*om*I/lam;
 auto prof=[&](double x){return sqrt(2*kap*kap/(1+d*cosh(2*kap*x)));};
 double r2=0,ii=0;for(double x=-150;x<=150;x+=.002){double f=prof(x);ii+=f*f*.002;r2+=x*x*f*f*.002;} double R=sqrt(r2/ii),w=wr*R,A=sqrt(lam*Q/(2*nu*w*sqrt(M_PI)));
 double L=ceil((T+max(90.,10*w))/dx)*dx; int N=2*lround(L/dx)+1,mid=N/2,nt=lround(T/dt);dt=T/nt;
 vector<double> u(N),z(N),v(N),y(N),a(N),b(N),zz(N),an(N);bool neutral=frac!=0; bool symmetric_neutral=frac<0; frac=abs(frac);
 double phase=argc>11?stod(argv[11]):0,sep=argc>12?stod(argv[12]):80.;
 if(mode=="readout" || mode=="restart" || mode=="formed"){
  ifstream in(argv[10],ios::binary);int n0;double h0;in.read((char*)&n0,sizeof(int));in.read((char*)&h0,sizeof(double)); vector<double> raw(4*n0);in.read((char*)raw.data(),raw.size()*sizeof(double));
  if(!in){cerr<<"input failed\n";return 2;}
  auto sample=[&](int c,double x){double j=x/h0+n0/2;int k=floor(j);if(k<0||k+1>=n0)return 0.;double g=j-k;return (1-g)*raw[c*n0+k]+g*raw[c*n0+k+1];};
  // Compact smooth extraction preserves declared finite Cauchy data; no analytic Q-ball replacement.
  auto taper=[](double x){x=abs(x);if(x<=12)return 1.;if(x>=18)return 0.;return .5*(1+cos(M_PI*(x-12)/6));};
  for(int j=1;j<N-1;j++){double x=(j-mid)*dx;
   if(mode=="restart"||mode=="formed"){double tap=mode=="formed"?taper(x):1.;u[j]=sample(0,x)*tap;z[j]=sample(1,x)*tap;v[j]=sample(2,x)*tap;y[j]=sample(3,x)*tap;continue;}
   // Two inward-moving, formed cores. Declared phase-gradient/velocity kick, not an exact Lorentz boost.
   for(int side=-1;side<=1;side+=2){double xx=x-side*sep,beta=-side*.15,k=om*beta,ph=k*xx+(side==1?phase:0),c=cos(ph),s=sin(ph),tap=taper(xx);
    double ur=sample(0,xx)*tap,ui=sample(1,xx)*tap;
    double vr=sample(2,xx)*tap-beta*(sample(0,xx+dx)*taper(xx+dx)-sample(0,xx-dx)*taper(xx-dx))/(2*dx);
    double vi=sample(3,xx)*tap-beta*(sample(1,xx+dx)*taper(xx+dx)-sample(1,xx-dx)*taper(xx-dx))/(2*dx);
    u[j]+=c*ur-s*ui;z[j]+=s*ur+c*ui;v[j]+=c*vr-s*vi;y[j]+=s*vr+c*vi;
   }
  }
 }else{
 for(int j=1;j<N-1;j++){double x=(j-mid)*dx,f=mode=="exact"||mode=="perturbed"?prof(x):A*exp(-x*x/(2*w*w));u[j]=f;y[j]=-(mode=="exact"||mode=="perturbed"?om:nu)*f;
 if(mode=="perturbed"){u[j]*=1+.02*exp(-x*x/8)*cos(1.3*x);v[j]=.01*f*sin(.7*x);}
 }}
 if(neutral){double sig=3,k=1,x0= mode=="gauss"?-30:-45; for(int j=0;j<N;j++){double xx=(j-mid)*dx-x0;a[j]=exp(-xx*xx/(2*sig*sig))*cos(k*xx); double ax=exp(-xx*xx/(2*sig*sig))*(-xx/(sig*sig)*cos(k*xx)-k*sin(k*xx));b[j]=-(1+eps*(u[j]*u[j]+z[j]*z[j]))*ax;}
 if(symmetric_neutral){auto aa=a,bb=b;for(int j=0;j<N;j++){a[j]+=aa[N-1-j];b[j]+=bb[N-1-j];}}
 double en=0;for(int j=1;j<N-1;j++){double Z=1+eps*(u[j]*u[j]+z[j]*z[j]),ar=(a[j+1]-a[j])/dx;double Zr=1+eps*(u[j+1]*u[j+1]+z[j+1]*z[j+1]);en+=dx/lam*(b[j]*b[j]/(2*Z)+(Z+Zr)*ar*ar/4);}
 double E=((om*om+.75)*I+.25*tanh(I))/lam,scale=sqrt(frac*E/en);for(int j=0;j<N;j++){a[j]*=scale;b[j]*=scale;}}
 ofstream log(out+".csv"),snap(out+"_snap.bin",ios::binary);log<<setprecision(15)<<"t,E,Q,P,Ea";for(int W:{20,30,40})log<<",E"<<W<<",Q"<<W<<",I"<<W<<",R"<<W<<",phase"<<W<<",freq"<<W;log<<",fluxE,fluxQ,center,leftE,rightE,midDensity,fluxEcum,fluxQcum\n";
 int obs=max(1,(int)lround(.2/dt)),snstep=max(1,(int)lround(10/dt));int ns=2*lround(120/dx)+1;snap.write((char*)&ns,sizeof(int));snap.write((char*)&dx,sizeof(double));
 auto boundary_flux=[&](int j){double ans=-((v[j]+v[j+1])*(u[j+1]-u[j])+(y[j]+y[j+1])*(z[j+1]-z[j]))/(lam*dx);if(neutral){double Z=1+eps*(u[j]*u[j]+z[j]*z[j]),Zr=1+eps*(u[j+1]*u[j+1]+z[j+1]*z[j+1]);double dz=2*eps*(u[j]*v[j]+z[j]*y[j]),dzr=2*eps*(u[j+1]*v[j+1]+z[j+1]*y[j+1]);double g=(a[j+1]-a[j])/dx;ans-=(Z+Zr)/4*g*(b[j]/Z+b[j+1]/Zr)/lam;ans+=dx*(dz-dzr)*g*g/(8*lam);}return ans;};
 auto boundary_q=[&](int j){return 2*(u[j]*z[j+1]-z[j]*u[j+1])/(lam*dx);};
 int fl=mid-lround(30/dx)-1,fr=mid+lround(30/dx);double FE=0,FQ=0,oldfe=boundary_flux(fr)-boundary_flux(fl),oldfq=boundary_q(fr)-boundary_q(fl);
 auto diagnostics=[&](int step){double E=0,q=0,p=0,ea=0,EC[3]={},QC[3]={},IC[3]={},RX[3]={},re[3]={},im[3]={},freq[3]={},xe=0,le=0,ri=0;
 for(int j=1;j<N-1;j++){double x=(j-mid)*dx,s=u[j]*u[j]+z[j]*z[j],Z=1+eps*s,ur=(u[j+1]-u[j])/dx,zr=(z[j+1]-z[j])/dx,ul=(u[j]-u[j-1])/dx,zl=(z[j]-z[j-1])/dx;
 double dena=0;if(neutral){double ar=(a[j+1]-a[j])/dx,al=(a[j]-a[j-1])/dx,Zr=1+eps*(u[j+1]*u[j+1]+z[j+1]*z[j+1]),Zl=1+eps*(u[j-1]*u[j-1]+z[j-1]*z[j-1]);dena=(b[j]*b[j]/(2*Z)+(Z+Zr)*ar*ar/8+(Z+Zl)*al*al/8)/lam;}
 double den=(v[j]*v[j]+y[j]*y[j]+.5*(ur*ur+zr*zr+ul*ul+zl*zl)+s-s*s+s*s*s)/lam+dena,qd=2*(z[j]*v[j]-u[j]*y[j])/lam;
 E+=dx*den;ea+=dx*dena;q+=dx*qd;p-=dx/lam*(v[j]*(ur+ul)+y[j]*(zr+zl)+(neutral?b[j]*(a[j+1]-a[j-1])/(2*dx):0));xe+=dx*x*den;
 if(x<0)le+=dx*den;else ri+=dx*den;
 for(int c=0;c<3;c++)if(abs(x)<20+10*c+dx/4){EC[c]+=dx*den;QC[c]+=dx*qd;IC[c]+=dx*s;RX[c]+=dx*x*x*s;double f=prof(x);re[c]+=dx*f*u[j];im[c]+=dx*f*z[j];freq[c]+=dx*(z[j]*v[j]-u[j]*y[j]);}}
 // Exact continuous-time lattice flux for node-centered energy (half bond per node).
 auto ef=[&](int j){double ans=-((v[j]+v[j+1])*(u[j+1]-u[j])+(y[j]+y[j+1])*(z[j+1]-z[j]))/(lam*dx);if(neutral){double Z=1+eps*(u[j]*u[j]+z[j]*z[j]),Zr=1+eps*(u[j+1]*u[j+1]+z[j+1]*z[j+1]);double dz=2*eps*(u[j]*v[j]+z[j]*y[j]),dzr=2*eps*(u[j+1]*v[j+1]+z[j+1]*y[j+1]);double g=(a[j+1]-a[j])/dx;ans-=(Z+Zr)/4*g*(b[j]/Z+b[j+1]/Zr)/lam;ans+=dx*(dz-dzr)*g*g/(8*lam);}return ans;};
 auto qf=[&](int j){return 2*(u[j]*z[j+1]-z[j]*u[j+1])/(lam*dx);};int jl=mid-lround(30/dx),jr=mid+lround(30/dx);
 log<<step*dt<<","<<E<<","<<q<<","<<p<<","<<ea;for(int c=0;c<3;c++)log<<","<<EC[c]<<","<<QC[c]<<","<<IC[c]<<","<<sqrt(RX[c]/max(IC[c],1e-300))<<","<<atan2(im[c],re[c])<<","<<freq[c]/max(IC[c],1e-300);
 log<<","<<ef(jr)-ef(jl-1)<<","<<qf(jr)-qf(jl-1)<<","<<xe/E<<","<<le<<","<<ri<<","<<u[mid]*u[mid]+z[mid]*z[mid]<<","<<FE<<","<<FQ<<"\n";
 };
 for(int step=0;step<=nt;step++){
 double newfe=boundary_flux(fr)-boundary_flux(fl),newfq=boundary_q(fr)-boundary_q(fl);if(step){FE+=.5*dt*(newfe+oldfe);FQ+=.5*dt*(newfq+oldfq);}oldfe=newfe;oldfq=newfq;
 if(step%obs==0||step==nt)diagnostics(step);
 if(step%snstep==0||step==nt){double t=step*dt;snap.write((char*)&t,sizeof(double));for(auto*vv:{&u,&z,&v,&y})snap.write((char*)(vv->data()+mid-ns/2),ns*sizeof(double));}
 if(step==nt)break;
 for(int j=1;j<N-1;j++){u[j]+=.5*dt*v[j];z[j]+=.5*dt*y[j];}
 if(neutral){for(int j=0;j<N;j++)zz[j]=1+eps*(u[j]*u[j]+z[j]*z[j]);for(int j=1;j<N-1;j++){a[j]+=.5*dt*b[j]/zz[j];double f=.25*dt*eps*b[j]*b[j]/(zz[j]*zz[j]);v[j]+=f*u[j];y[j]+=f*z[j];}}
 for(int j=1;j<N-1;j++){double s=u[j]*u[j]+z[j]*z[j],f=-(1-2*s+3*s*s);if(neutral){double ar=(a[j+1]-a[j])/dx,al=(a[j]-a[j-1])/dx;f-=eps*(ar*ar+al*al)/4;b[j]+=dt*((zz[j]+zz[j+1])*ar-(zz[j]+zz[j-1])*al)/(2*dx);}
 v[j]+=dt*((u[j+1]-2*u[j]+u[j-1])/(dx*dx)+f*u[j]);y[j]+=dt*((z[j+1]-2*z[j]+z[j-1])/(dx*dx)+f*z[j]);}
 if(neutral)for(int j=1;j<N-1;j++){a[j]+=.5*dt*b[j]/zz[j];double f=.25*dt*eps*b[j]*b[j]/(zz[j]*zz[j]);v[j]+=f*u[j];y[j]+=f*z[j];}
 for(int j=1;j<N-1;j++){u[j]+=.5*dt*v[j];z[j]+=.5*dt*y[j];}
 }
 log.flush();snap.flush();if(!log||!snap){cerr<<"diagnostic write failed\n";return 3;}log.close();snap.close();
 ofstream fin(out+"_final.bin",ios::binary);fin.write((char*)&N,sizeof(int));fin.write((char*)&dx,sizeof(double));for(auto*vv:{&u,&z,&v,&y})fin.write((char*)vv->data(),N*sizeof(double));
 fin.flush();if(!fin){cerr<<"state write failed\n";return 4;}fin.close();
 ofstream meta(out+"_meta.json");meta<<setprecision(15)<<"{\"omega\":"<<om<<",\"width_ratio\":"<<wr<<",\"nu\":"<<nu<<",\"dx\":"<<dx<<",\"dt\":"<<dt<<",\"T\":"<<T<<",\"L\":"<<L<<",\"Q_target\":"<<Q<<",\"R_target\":"<<R<<",\"w\":"<<w<<",\"mode\":\""<<mode<<"\",\"neutral_fraction\":"<<frac<<",\"symmetric_neutral\":"<<(symmetric_neutral?"true":"false")<<",\"phase\":"<<phase<<",\"separation\":"<<sep<<"}";
}
