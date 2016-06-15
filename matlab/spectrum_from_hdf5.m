%taking ACF directly from hdf5 files
% function spectrum_from_hdf5(root,varargin)
% p = inputParser;
% addOptional(p,'extpat','.dt3.h5')
% parse(p,varargin{:})
% U = p.Results;
% %%
% root = expanduser(root);
% flist = dir([root,filesep,'*',U.extpat]);   
% flist=sort({flist.name});
% 
% for fn=flist
%     
%   [range,spec,tInd,dtime,BeamcodeMap,beamcode] = loadspec([root,filesep,fn{1}]);
%   pause
% 
% end %for fn
% end %function

function [range,spec,tInd,dtime,BeamcodeMap,beamcode] = spectrum_from_hdf5(filename)

range = h5read(filename,'/S/Data/Acf/Range');
Mtime = h5read(filename,'/Time/MatlabTime');
BeamcodeMap = h5read(filename,'/Setup/BeamcodeMap');
dnt=size(Mtime,2);
dnr=length(range);
dns=1071/3;

index=zeros(dnt,1);

bdata= h5read(filename,'/S/Data/Beamcodes'); % Matrix of positions (beams) performed by the radar
beamcode=64157;
% beamcode=bdata(11,1)
for i=1:dnt
    index(i)=find(bdata(:,i)==beamcode);
end


ACF = h5read(filename,'/S/Data/Acf/Data');% Matrix of ACF
ACF_Noise = h5read(filename,'/S/Noise/Acf/Data'); % ACF for noise

dtime=datetime(Mtime(1,:),'ConvertFrom','datenum');

% for what records (times) do you want the spectrum? 
%each file contains 50 records, each in this experiment worth of 5 seconds of data
tInd=(20:1:30);  
for ti=1:length(tInd) 
    spec = timeproc(ti,tInd,index,dns,range,ACF,ACF_Noise);
    plotspectrum(range,spec,ti,tInd,dtime,BeamcodeMap,beamcode)
end %for tt

end % function

function spec = timeproc(ti,tInd,index,dns,range,ACF,ACF_Noise)
Nlag=16;
acf=zeros(length(range),Nlag);
spec=zeros(length(range),2*Nlag-1);
acf_noise=zeros(size(ACF_Noise,2),Nlag);
spec_noise=zeros(1,31);

        
% here decide how many records to average to calculate the spectrum, I think each record is 5 seconds worth of data
for ave=tInd(ti):tInd(ti)+1
    acf=acf+squeeze(ACF(1,:,:,index(ave),ave)+1j*ACF(2,:,:,index(ave),ave));
    acf_noise=acf_noise+squeeze(ACF_Noise(1,:,:,index(ave),ave)+...
                              1j*ACF_Noise(2,:,:,index(ave),ave));
end
acf=acf/dns/(ave-tInd(ti)+1);
acf_noise=acf_noise/dns/(ave-tInd(ti)+1);

for i=1:size(ACF_Noise,2)
    spec_noise=spec_noise + fftshift(fft([conj(fliplr(acf_noise(i,2:16))),  acf_noise(i,:)]));
end
spec_noise=spec_noise/i;

for i=1:length(range)
    % calculate the spectrum from ACF
    spec(i,:)=fftshift(fft([conj(fliplr(acf(i,2:16))) acf(i,:)]))-spec_noise; 
end

end %function

function plotspectrum(range,spec,ti,tInd,dtime,BeamcodeMap,beamcode)

AZEL = BeamcodeMap(2:3, BeamcodeMap(1,:)==beamcode); %retrieves az,el

if false
    llim=100; step=15; ulim=165;
    spec_ave=zeros(length(llim:step:ulim),31);
    counter=1;
    figure; hold on
    for i=[145]
        spec_ave(counter,:)=sum(spec(i-10:i+5,:),1)/16;
        plot(freqaxis,abs(spec_ave(counter,:)))
        xlabel('Frequency (kHz)')
        ylabel('Amplitude')
        title(['Altitude: ' num2str(round(range(i+round(step/2))*sind(AZEL(2))/1e3))]);
        counter=counter+1;
    end
end %if
%%
ir= range*sind(AZEL(2)) > 60e3; %altitude over N km
freqaxis=linspace(-100/6,100/6,31); %kHz%%

figure
imagesc(freqaxis,...
        transpose(range(ir)*sind(AZEL(2))/1000),...
        10*log10(abs(spec(ir,:))));
caxis([10,35])
 
set(gca,'YDir','normal')
xlabel('Frequency (kHz)')
ylabel('Altitude (km)')
title([datestr(dtime(1,tInd(ti))),...
        ' El: ' num2str(AZEL(2)) ' Az: ' num2str(round(AZEL(1)))])
cb = colorbar();
ylabel(cb,'dB')

end %function