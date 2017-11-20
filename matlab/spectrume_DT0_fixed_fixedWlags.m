function spectrum_lags(filename)
%filename='d0281239.dt0.h5';

rdf=1;
tdf=1;
data = cast(hdf5read(filename,'/IncohCodeFl/Data/Acf/Data'),'double');
lags_sum = cast(hdf5read(filename,'/IncohCodeFl/Data/Acf/Lagmat'),'double');
bdata= cast(hdf5read(filename,'/IncohCodeFl/Data/Beamcodes'),'double'); 
range = cast(hdf5read(filename,'/IncohCodeFl/Data/Acf/Range'),'double');
zero_lag_power = cast(hdf5read(filename,'/S/ZeroLags/Power/Data'),'double');
Wlag = cast(hdf5read(filename,'/Setup/Ambiguity/A16_30_10/WlagSum'),'double');

beamcode=64157;
index=zeros(50,1);


for i=1:50
    index(i)=find(bdata(:,i)==beamcode);
end
clear bdata;


pulse=35; %number of pulse=time=record
for pulse=23:38
for jj=1:300 %different ranges
lags=zeros(1,48);
lags_rep=zeros(1,48);
for ii=1:76
    lags_rep(lags_sum(ii)+1)=lags_rep(lags_sum(ii)+1)+1;
    lags(lags_sum(ii)+1)=lags(lags_sum(ii)+1)+(data(1,jj,ii,index(pulse),pulse)+j*data(2,jj,ii,index(pulse),pulse))/Wlag(ii);
end
x(:,jj)=lags./lags_rep;
x(1,jj)=zero_lag_power(jj,index(pulse),pulse)/0.9259392*16;
end
x=x/96;
for jj=1:300
    x(:,jj)=x(:,jj)-x(:,300);
end


rrrr((48:95),:)=x;
for looloo=1:47
rrrr(looloo,:)=real(x(49-looloo,:))-j*imag(x(49-looloo,:));
end


yy=zeros(300,95);
for i=1:300
yy(i,:)=10*log10(abs(fftshift(fft(rrrr(:,i)))));
end
freqaxis=linspace(-100/2,100/2,95);
rindex=find(range>80000);
figure;
imagesc(freqaxis,range(rindex)/1000,yy(rindex,:));
%caxis([25,60]);
set(gca,'YDir','normal')
xlabel('kHz');
ylabel('km');
title(['record ',num2str(pulse)])
colormap('jet');
colorbar();
end

end %function
