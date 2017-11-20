function power_DT3(root,varargin)

p = inputParser;
addOptional(p,'extpat','.dt3.h5')
parse(p,varargin{:})
U = p.Results;
%%
root = expanduser(root);
flist = dir([root,filesep,'*',U.extpat]);   
flist=sort({flist.name});
%%
i=1;
dtime = datetime(nan,'convertfrom','datenum');
power = [];
for fn=flist   % goes through multiple hdf5 files and plot the data in one image
    [t,range,pow,coord]=loaddt([root,filesep,fn{1}]);
    cind = (i-1)*length(t)+1:i*length(t);
    dtime(cind) = t;
    power(:,cind) = pow;
    i=i+1;
end

    plotdt(dtime,range,power,coord)

end %function

function [dtime,range,power,coord] = loaddt(filename)

rdf=1;
tdf=1;

range = h5read(filename,'/Raw11/RawData/Power/Range');
time = h5read(filename,'/Time/MatlabTime');
t=size(time);
dnr=floor(length(range)/rdf);
dnt=floor(t(2)/tdf);
try
    dns = hdf5read(filename,'/S/Data/PulsesIntegrated'); % TODO: is this correct?
    dns = double(dns(1));
catch
    dns=355/5;  % this is the number of pulses per beam in each record that changes experiment to experiment
end
%%
index=zeros(dnt,dns);
% Matrix of positions (beams and beamcodes and AZ and EL angles)
bdata= h5read(filename,'/Raw11/RawData/RadacHeader/BeamCode'); 

% choose radar beam, you can see beamcodes for the beams in the experiment in hdf5 files at Raw11\Rawdata\Beamcodes. 
% 64157 is the "up B" magnetic zenith beam
beamcode=64157;  
for i=1:dnt
    index(i,:)=find(bdata(:,i)==beamcode);
end
%clear bdata
%b=size(index);

power = calcpower(filename,dnr,dnt,dns,index);
%%
bcode = h5read(filename,'/Setup/BeamcodeMap');
bindex=find(bcode(1,:)==beamcode);
coord=['    AZ = ' num2str(bcode(2,bindex)) '  EL = ' num2str(bcode(3,bindex))];

dtime = datetime(time(1,:),'ConvertFrom','datenum');

end %function

function power = calcpower(fn,dnr,dnt,dns,index)

%raw complex voltages I+jQ
data = h5read(fn,'/Raw11/RawData/Samples/Data');
%s=size(data);

%nb=s(3)/b(2);
power = nan(dnr,dnt,'like',data);
for ir=1:dnr  % range or altitude
   for it=1:dnt  % dnt is the number of records in each file (they use records as unit of time)
      % dns is the number of transmitted pulses in each record
      % so here we are calculating the power from complex voltages and
      % averaging over dns pulses in each record so each time bin in
      % produced plot corresponds to one record. Note that in this
      % experiment they have calculated the power from voltages and
      % stored them at S\Data\Power\Data so you can not calculate and
      % get them from there (faster)
      auxd= sum(data(1,ir,index(it,:),it).^2 + data(2,ir,index(it,:),it).^2);
      power(ir,it)=auxd/dns; 
   end
end

end

function plotdt(dtime,range,power,coord)

rindex=find(range>80000);
%figname=['powDt3-' num2str(beamcode)];
figure
imagesc(datenum(dtime),...
         range(rindex)*1e-3,...
         10*log10(power(rindex,:)));
datetick('x')
axis('xy','tight')
colorbar()
day = char(dtime(1));  day=day(1:12);
title([day coord])
xlabel('UTC')
ylabel('Range [km]')

end 
