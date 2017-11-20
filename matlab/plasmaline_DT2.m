function plasmaline_DT2(filename,varargin)
%%
%calculation of auto correlation function from DT0
p = inputParser;
addOptional(p,'beamcode',64157)
parse(p,varargin{:})
U = p.Results;
%% load data from HDF5

%Matrix containing the autocorrelation of the data
data = hdf5read(filename,'/PLFFTS/Data/Spectra/Data');
%Matrix of positions (beams) performed by the radar
bdata = hdf5read(filename,'/PLFFTS/Data/Beamcodes'); 

freq  = hdf5read(filename,'/PLFFTS/Data/Spectra/Frequency');
range = hdf5read(filename,'/PLFFTS/Data/Spectra/Range');

index=zeros(50,1);
freq=(freq+5*10^6); %dt2 is upshifted

for i=1:15
    index(i)=find(bdata(:,i)==U.beamcode);
end

for pulse=1:15
    noise=data(16,:,index(pulse),pulse); noise_power=sum(noise);   
    for ii=1:16 %ranges
        %x(ii,jj-33)=data(1,jj,16*10*(pulse-1)+ii)+j*data(2,jj,16*10*(pulse-1)+ii);
        x(ii,:)=data(ii,:,index(pulse),pulse);%-noise;
    end %for

    plotplasmaline(x,freq,range,pulse)

end %for

end %function

function plotplasmaline(data,freq,range,pulse)

figure
imagesc(freq/10^6,range(4:15)/10^3,10*log10(abs(data(4:15,:)/10)));
%caxis([40,78]);
set(gca,'YDir','normal')
xlabel('MHz')
ylabel('Km')
title(['record ',num2str(pulse)])
colorbar()

if false
    figure;
    plot(freq/10^6,10*log10(abs(data(8,:)/1)),'b');
    title(['Record ',num2str(pulse),'   Up-Shifted']);
    xlabel('Frequency (MHz)');
    ylabel('Intensity (dB)');
    hold on
    plot(freq/10^6,10*log10(abs(data(9,:)/1)),'r');
    plot(freq/10^6,10*log10(abs(data(10,:)/1)),'g');
end %if
end %function