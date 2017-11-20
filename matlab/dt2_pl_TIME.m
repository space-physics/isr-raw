clear all;
start_file=357;
end_file=430; 

for oo=start_file:end_file


filename=['d0326' num2str(oo) '.dt2.h5'];


data = cast(hdf5read(filename,'/PLFFTS/Data/Spectra/Data'),'double');%Matrix containing the autocorrelation of the data
freq = cast(hdf5read(filename,'/PLFFTS/Data/Spectra/Frequency'),'double');
bdata= cast(hdf5read(filename,'/PLFFTS/Data/Beamcodes'),'double'); %Matrix of positions (beams) performed by the radar
range = cast(hdf5read(filename,'/PLFFTS/Data/Spectra/Range'),'double');
time = cast(hdf5read(filename,'/Time/MatlabTime'),'double');
[tt t]=size(time);
beamcode=64157;
index=zeros(t,1);
freq=freq+5*10^6; %dt1 is downshifted

for i=1:t
    index(i)=find(bdata(:,i)==beamcode);
end
clear bdata;


for pulse=1:t
noise=data(16,:,index(pulse),pulse); noise_power=sum(noise);    
for ii=4:10 %different ranges
    %x(ii,jj-33)=data(1,jj,16*10*(pulse-1)+ii)+j*data(2,jj,16*10*(pulse-1)+ii);
    x(ii,(oo-start_file)*t+pulse,:)=data(ii,:,index(pulse),pulse)-noise;

end
TIME((oo-start_file)*t+pulse)=(oo-start_file)*t+pulse;
end
end
bcode = cast(hdf5read(filename,'/Setup/BeamcodeMap'),'double');
bindex=find(bcode(1,:)==beamcode);
coord=['    AZ = ' num2str(bcode(2,bindex)) '  EL = ' num2str(bcode(3,bindex))];


iji=9;
figure;
imagesc(freq/10^6,TIME,10*log10(abs(squeeze(x(iji,:,:)))));
%caxis([40,78]);
set(gca,'YDir','normal')
xlabel('Frquency (MHz)');
ylabel(['Time (records) after file ' num2str(start_file)]);
title(['Range: ' num2str(round(range(iji)/1000)) '(km), ' coord]);
colormap('jet');
colorbar();
% figure;
% plot(freq/10^6,10*log10(abs(x(8,:)/1)),'b');
% title(['Record ',num2str(pulse),'   Down-Shifted']);
% xlabel('Frequency (MHz)');
% ylabel('Intensity (dB)');
% hold on
% plot(freq/10^6,10*log10(abs(x(9,:)/1)),'r');
% plot(freq/10^6,10*log10(abs(x(10,:)/1)),'g');
% hold off
