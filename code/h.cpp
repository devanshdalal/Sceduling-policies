#include<stdio.h>
#include<string.h>
#include<iostream>
#include<algorithm>
#include<map>
#include<cmath>
#include<vector>
using namespace std;
typedef unsigned long long ul;
typedef long long ll;
typedef double ld;

ll a[100],c[100],it[100];
ll mem[21][201][21];
ll fact[21];
ll n,k;

ll gcd1(ll x,ll y){
    if(y==0)return x;
    else return gcd1(y,x%y);
}

ll max(ll a , ll b){
	return a>b? a:b;
}

inline ll gcd2(ll n1, ll n2) {
    ll tmp;
    while (n2 ) {
        tmp = n1;
        n1 = n2;
        n2 = tmp % n2;
    }
    return n1;
}

void g(){
	ll sum=a[0],l=1;
	mem[0][a[0]][1]=1;
	for (int i=0; i < n-1 ; ++i)
	{
		sum+=a[i+1];
		cout << "sum" << sum << endl;
		for (int j = 1; j <= sum ; j++)
		{
			// for (int l = 1; l <=i ; l++)
			// {
				mem[i+1][j][l]=mem[i][j][l];
				cout << mem[i][j][l] << "endl";
			// }
		}
		mem[i+1][a[i+1]][l]+=1;
		cout << endl;
		for (int j = 1; j <= sum ; j++)
		{
			// for (int l = 1; l <=i ; l++)
			// {
				mem[i+1][j+a[i+1]][l]+=mem[i][j][l];
			// }
		}
		cout << "-----------------------------------";
		for (int j = 1; j <= sum ; j++)
		{
			// for (int l = 1; l <=i ; l++)
			// {
			cout << mem[i+1][j][l] << " ";
			// }
		}
		cout << endl;
	}
}

ld cal(int s1,int s2){
	ll i,j=1,kk,nn=n-2,sum=0;
	for (i = 0; i < n; ++i)
	{
		if(i==s1 or i==s2)continue;
		it[j++]=a[i];
		sum+=a[i];
	}
	for (int j = 1; j <= sum ; j++)
	{
		for (int l = 1; l <=2 ; l++)
		{
			mem[0][j][l]=mem[1][j][l]=0;
		}
	}

	cout << "check1 "<< nn << endl;
	mem[1][it[1]][1]=1;
	sum=it[0];
	for ( i=2; i <= nn ; ++i)
	{
		for (int j = 1; j <= sum ; j++)
		{
			for (int l = 1; l <=i-1 ; l++)
			{
				mem[i][j][l]=mem[i-1][j][l];
			}
		}
		sum+=it[i];
		mem[i][it[i]][1]+=1;
		for (int j = 1; j <= sum ; j++)
		{
			for (int l = 1; l <=i ; l++)
			{
				mem[i][j+it[i]][l+1]+=mem[i-1][j][l];
			}
		}
		cout << "jj "<< sum <<" l "<< i <<endl;
		for (int j = 1; j <=  sum ; j++)
		{
			for (int l = 1; l <=i ; l++)
			{
				cout << "mem[" <<i<<"]["<<j<<"]["<<l<<"]=" << mem[i][j][l] << endl;
			}
		}
	}
	cout << "check2 " << endl;
	ld ans=0;
	cout << k<<" "<<a[s1]<<" "<<a[s2] << endl;
	cout << k-a[s1]-a[s2] << endl;
	for (int j = max(0,k-a[s1]-a[s2]); j < k ; j++)
	{
		for (int l = 0; l <= nn ; l++)
		{
			cerr<< "inside" << j <<" " << k << " "<< n << endl;
			ll num=(k-j- max(k-a[s1]-j,0) - max(k-a[s2]-j,0) )*(nn-l+1)*fact[nn-l]*fact[l]*2; 
			cout << "num " << num << endl;
			cout << "num " << k<<j<<(max(k-a[s1]-j,0))<<(max(k-a[s2]-j,0)) << endl;
			ll den = fact[n];
			ld res=ld(num)/ld(den);
			cout << res << endl;
			if(mem[nn][j][l]) cout << "dhsssssssjjj mem["<<nn<<"]["<<j<<"]["<<l<<"]"<< mem[nn][j][l] << endl;
			cout << "mem["<<nn<<"]["<<j<<"]["<<l<<"]" << mem[nn][j][l] << endl;
			ans+=(l==0 and j==0?res:mem[nn][j][l]*res);
			cout<< "ans " << ans << endl;
		}
	}
	return ans;
}

int main(){
    int t,i,j,l,m;
    for (i =fact[0]=1; i < 21; ++i)
    {
    	fact[i]=ll(i)*fact[i-1];
    }
    scanf("%d",&t);
    while(t--){
        scanf("%lld%lld",&n,&k);
        for (i = 0; i < n ; ++i)
        {
            scanf("%lld%lld",&a[i],&c[i]);
        }
        ld ans=0;
        for (i = 0; i <n ; ++i)
        {
        	for (j = i+1; j < n; j++)
        	{
        		if ( c[i]==c[j] )
        		{
        			cout << "hrtr " << endl;
        			ans+=cal(i,j);
        		}
        	}
        }
        printf("%lf\n", ans );

    }

    return 0;
}