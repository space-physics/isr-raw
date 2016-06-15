%in this file there is no averaging over pulses so much better time
%resolution on power

%TODO: Load only needed times

function power_zoom_Dt3(root,varargin)
p = inputParser;
addOptional(p,'extpat','.dt3.h5')
addOptional(p,'beamcode',64157)
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
for fn=flist %goes through all files
    [pow,range,t,rindex,coord] = loaddt([root,filesep,fn{1}],U.beamcode);
    
    tind = (i-1)*length(t)+1:i*length(t);
    dtime(tind) = t;
    
    pind = (i-1)*size(pow,2)+1:i*size(pow,2);
    power(:,pind) = pow;
    i=i+1;
end %for fn

plotdt(power,range,dtime,rindex,coord,false)

end %function

function [power,range,dtime,rindex,coord] = loaddt(filename,beamcode)
disp(filename)

rdf=1;
tdf=1;

range = h5read(filename,'/Raw11/RawData/Power/Range');
time = h5read(filename,'/Time/MatlabTime');
t=size(time,2);
dnr=floor(size(range,1)/rdf);
dnt=floor(t/tdf);
dns=355/5;
%%
%dtime = datetime(time(1,:),'ConvertFrom','datenum');
index=zeros(dnt,dns);

i=0;
for it=1:dnt
   dt=(time(2,it)-time(1,it))/dns; 
   for is=1:dns
      aux=time(1,it)+(is-1)*dt;
      i=i+1;
      dtime(i)=aux;
   end
end

dtime = datetime(dtime,'ConvertFrom','datenum');
%%
bdata= h5read(filename,'/Raw11/RawData/RadacHeader/BeamCode'); %Matrix of beams

for i=1:dnt
    index(i,:)=find(bdata(:,i)==beamcode);
end

power = calcpower(filename,dnr,dnt,dns,index);


bcode = h5read(filename,'/Setup/BeamcodeMap');
bindex=find(bcode(1,:)==beamcode);
coord=['    AZ = ' num2str(bcode(2,bindex)) '  EL = ' num2str(bcode(3,bindex))];

rindex=find(range>80000);

Noise=mean(mean(power(186:196,:),1),2);
power=(power-Noise);

power(rindex,:)=bsxfun(@times,power(rindex,:),range(rindex).^2);

end %function

function power = calcpower(fn,dnr,dnt,dns,index)

data = h5read(fn,'/Raw11/RawData/Samples/Data'); % I+jQ
%power = nan(dnr,dns*dnt,'like',data);
power = nan(dnr,dns*dnt,'like',data);

i=0;
for it=1:dnt
  %auxd=0;
  for is=1:dns
      i=i+1;
      for ir=1:dnr
         %power(ir,is*it)
         power(ir,i)=(data(1,ir,index(it,is),it).^2+...
                       data(2,ir,index(it,is),it).^2);
         %auxd=auxd+abs(data(1,ir,index(it,is),it));
      end
  end
  %power(ir,it)=auxd/dns;
end

end %function



function plotdt(power,range,dtime,rindex,coord,dolog)

figure
if dolog
    imagesc(datenum(dtime),range(rindex)*1e-3,...
            10*log10(abs(power(rindex,:))))
	caxis([100 150])
else
    imagesc(datenum(dtime),...
             range(rindex)*1e-3,...
             abs(power(rindex,:)))
    caxis([0.001 50]*10^14)
end

colorbar()
axis('xy')


set(gca,'xlim',[datenum(2011,3,1,10,5,0),datenum(2011,3,1,10,8,0)])
datetick('x','keepticks')


day = char(dtime(1));    day = day(1:12);
title([day coord])
xlabel('UTC')
ylabel('Range [km]')
%datetick('x','HH:MM:SS','keepticks')

end %function