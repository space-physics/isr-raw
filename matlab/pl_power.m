clear all
%%%%%%%%%%%%%%%%%%---------------------------------------------------------
%calculation of auto correlation function from DT0

filename='d0281239.dt2.h5';
data = cast(hdf5read(filename,'/PLFFTS/Data/Power/Data'),'double');%Matrix containing the autocorrelation of the data
freq = cast(hdf5read(filename,'/PLFFTS/Data/Spectra/Frequency'),'double');
bdata= cast(hdf5read(filename,'/PLFFTS/Data/Beamcodes'),'double'); %Matrix of positions (beams) performed by the radar
range = cast(hdf5read(filename,'/PLFFTS/Data/Power/Range'),'double');
beamcode=64157;
index=zeros(50,1);
freq=(freq+5*10^6); %dt2 is upshifted

for i=1:50
    index(i)=find(bdata(:,i)==beamcode);
end
clear bdata;


for pulse=20:40

%for ii=3155:16700 %ranges
    %x(ii,jj-33)=data(1,jj,16*10*(pulse-1)+ii)+j*data(2,jj,16*10*(pulse-1)+ii);
    x(:,pulse-19)=data((3155:16700),index(pulse),pulse);
%end
end


figure;
imagesc((20:1:40),range(3155:16700)/10^3,10*log10(abs(x)));
%caxis([40,78]);
set(gca,'YDir','normal')
xlabel('records');
ylabel('Km');
title(['record ',num2str(pulse)])
colormap('jet');
colorbar();
% figure;
% plot(freq/10^6,10*log10(abs(x(8,:)/1)),'b');
% title(['Record ',num2str(pulse),'   Up-Shifted']);
% xlabel('Frequency (MHz)');
% ylabel('Intensity (dB)');
% hold on
% plot(freq/10^6,10*log10(abs(x(9,:)/1)),'r');
% plot(freq/10^6,10*log10(abs(x(10,:)/1)),'g');
% hold off
