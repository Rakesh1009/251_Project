#include<simplecpp>

main_program{
int i=1,input;
cin >> input ;
for(i=1;i<=input;i++) {
 int s=0;
 for(int t=1;t<i;t++) {
 if(i%t==0) {s=s+t;};
 }
 if(s==i)
 cout<<s<< endl;
}
}
