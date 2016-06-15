clear all;
start_file=39;
end_file=41;
for oo=start_file:end_file

filename=['d02812' num2str(oo) '.dt0.h5'];
rdf=1;
tdf=1;

range = cast(hdf5read(filename,'/S/ZeroLags/Power/Range'),'double');
time = cast(hdf5read(filename,'/Time/MatlabTime'),'double');
t=size(time);
dnr=floor(size(range)/rdf);
dnt=floor(t(2)/tdf);
dns=1248/13;

index=zeros(dnt,dns);

bdata= cast(hdf5read(filename,'/S/ZeroLags/Beamcodes'),'double'); %Matrix of positions (beams) performed by the radar
beamcode=bdata(12,1);
for i=1:dnt
    index(i,:)=find(bdata(:,i)==beamcode);
end
clear bdata;
b=size(index);

data = cast(hdf5read(filename,'/S/ZeroLags/Power/Data'),'double');
s=size(data);

nb=s(3)/b(2);


   for it=1:dnt
            power(:,it+dnt*(oo-39))=data(:,index(it),it);
   end


clear data;

bcode = cast(hdf5read(filename,'/Setup/BeamcodeMap'),'double');
bindex=find(bcode(1,:)==beamcode);
coord=['    AZ = ' num2str(bcode(2,bindex)) '  EL = ' num2str(bcode(3,bindex))];

day=datestr(time(1,1)+(time(1,1)-time(2,1)),29);
for it=1:dnt         
%    aux=time(1,it);%+(time(1,it)-time(2,it));
%    Ntime(it+dnt*(oo-39))=str2double(datestr(aux,'HH'))+...
%             str2double(datestr(aux,'MM'))/60+...
%             str2double(datestr(aux,'SS'))/3600+...
%             str2double(datestr(aux,'FFF'))/3600000;

Ntime(it+dnt*(oo-39))=(start_file-37)*dnt+it+dnt*(oo-39); %time exis---> number of records
end
end
rindex=find(range>80000);
%figname=['powDt3-' num2str(beamcode)];
figure;
imagesc(Ntime,range(rindex)*1e-3,10*log10(power(rindex,:)));
axis xy;
caxis([45 55]);
colormap('jet');
colorbar();
title([day coord]);
xlabel('number of records from file 237. (each file contains 50 records)');
ylabel('Range [km]');
%print('-deps',[figname '.eps']);
%print('-dpng',[figname '.png']);
%close();

