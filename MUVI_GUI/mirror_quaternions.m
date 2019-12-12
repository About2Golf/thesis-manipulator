%% MUVI Manipulator Optical GSE Simulation
% Written by: Jason Grillo
% 10/28/2019

clear all, close all, clc

%% Define Unit Coordinate Vectors and Ray Intersection Length
unitx = [1 0 0];
unity = [0 1 0];
unitz = [0 0 1];
origin = [0 0 0];

l_focus = 10.823;   % mm

%% Define Rotation Quaternions
% PITCH or YAW
% mode = 'PITCH';  
mode = 'YAW';

theta = 30; % deg of rotation

if strcmp('PITCH',mode)
    q = [cosd(theta/2) unitx*sind(theta/2)];
    q_star = [cosd(theta/2) -unitx*sind(theta/2)];
else
    q = [cosd(theta/2) unitz*sind(theta/2)];
    q_star = [cosd(theta/2) -unitz*sind(theta/2)];
end

%% Define Initial Mirror Quaternions (mm)
% CAD Values
% r_bot1 = [0 -12.7 20.882 2.312];
% r_bot2 = [0 0 11.901 -6.669];
% r_bot3 = [0 12.7 20.882 2.312];
% r_top4 = [0 -25.4 23.324 37.204];
% r_top5 = [0 0 5.364 19.244];
% r_top6 = [0 25.4 23.324 37.204];
% beam1 = [0 0 80 32.45];
% beam2 = [0 0 18.57 32.45];
r_FOV1 = [0 0 12.359 -6.211];
r_FOV2 = [0 -7.876 18.57 0];
r_FOV3 = [0 0 29.329 10.759];
r_FOV4 = [0 0 5.501 19.381];
r_FOV5 = [0 -16.571 18.57 32.45];
r_FOV6 = [0 0 41.206 55.086];
r_iris1 = [0 -2.9 0 0];
r_iris2 = [0 0 0 -2.9];
r_iris3 = [0 0 0 2.9];
r_detc1 = [0 -10 -10.823 0];
r_detc2 = [0 0 -10.823 -10];
r_detc3 = [0 0 -10.823 10];

% Measured Values
r_bot1 = [0	-12.7191	21.6663	3.6961];
r_bot2 = [0	-0.4506	12.2728	-5.8707];
r_bot3 = [0	12.2255	21.2872	3.0825];
r_top4 = [0	-25.4325	23.8267	37.9334];
r_top5 = [0	-0.2472	5.8059	19.9078];		
r_top6 = [0	25.1571	23.8419	37.9761];	
beam1 = [0	0	17.9768	32.3248];
beam2 = [0	0	54.7426	32.3248];

p1 = [r_iris1(2:4);r_bot1(2:4);r_top4(2:4)];
p2 = [r_iris2(2:4);r_bot2(2:4);r_top5(2:4)];
p3 = [r_iris3(2:4);r_bot3(2:4);r_top6(2:4)];

[center, rad, v1, v2] = circlefit3d(p1,p2,p3);

%% Calculate Rotated Quaternions
r_bot1_prime = quatmultiply(quatmultiply(q,r_bot1),q_star);
r_bot2_prime = quatmultiply(quatmultiply(q,r_bot2),q_star);
r_bot3_prime = quatmultiply(quatmultiply(q,r_bot3),q_star);
r_top4_prime = quatmultiply(quatmultiply(q,r_top4),q_star);
r_top5_prime = quatmultiply(quatmultiply(q,r_top5),q_star);
r_top6_prime = quatmultiply(quatmultiply(q,r_top6),q_star);
r_FOV1_prime = quatmultiply(quatmultiply(q,r_FOV1),q_star);
r_FOV2_prime = quatmultiply(quatmultiply(q,r_FOV2),q_star);
r_FOV3_prime = quatmultiply(quatmultiply(q,r_FOV3),q_star);
r_FOV4_prime = quatmultiply(quatmultiply(q,r_FOV4),q_star);
r_FOV5_prime = quatmultiply(quatmultiply(q,r_FOV5),q_star);
r_FOV6_prime = quatmultiply(quatmultiply(q,r_FOV6),q_star);
r_iris1_prime = quatmultiply(quatmultiply(q,r_iris1),q_star);
r_iris2_prime = quatmultiply(quatmultiply(q,r_iris2),q_star);
r_iris3_prime = quatmultiply(quatmultiply(q,r_iris3),q_star);
r_detc1_prime = quatmultiply(quatmultiply(q,r_detc1),q_star);
r_detc2_prime = quatmultiply(quatmultiply(q,r_detc2),q_star);
r_detc3_prime = quatmultiply(quatmultiply(q,r_detc3),q_star);


p1_prime = [r_iris1_prime(2:4);r_bot1_prime(2:4);r_top4_prime(2:4);r_detc1_prime(2:4)];
p2_prime = [r_iris2_prime(2:4);r_bot2_prime(2:4);r_top5_prime(2:4);r_detc2_prime(2:4)];
p3_prime = [r_iris3_prime(2:4);r_bot3_prime(2:4);r_top6_prime(2:4);r_detc3_prime(2:4)];

[center_prime, rad_prime, v1_prime, v2_prime] = circlefit3d(p1_prime,p2_prime,p3_prime);

%% Calculate Normal Vectors to Mirrors
bot_mirror_norm = cross(r_bot1_prime(2:4)-r_bot2_prime(2:4),r_bot3_prime(2:4)-r_bot2_prime(2:4));
top_mirror_norm = cross(r_top4_prime(2:4)-r_top5_prime(2:4),r_top6_prime(2:4)-r_top5_prime(2:4));

bot_mirror_norm = bot_mirror_norm/norm(bot_mirror_norm);
top_mirror_norm = top_mirror_norm/norm(top_mirror_norm);

%% Calculate Beam Line Intersection Point on Top Mirror

norm = top_mirror_norm;
P0 = beam1(2:4);
P1 = beam2(2:4);
P2 = r_top4_prime(2:4);

t_top = (norm(1)*P0(1)-norm(1)*P2(1) + ...
            norm(2)*P0(2)-norm(2)*P2(2) + ...
                norm(3)*P0(3)-norm(3)*P2(3))/...
                    (norm(1)*P0(1)-norm(1)*P1(1)+...
                        norm(2)*P0(2)-norm(2)*P1(2)+...
                            norm(3)*P0(3)-norm(3)*P1(3));

top_ints_pt = [P0(1)+t_top*(P1(1)-P0(1)) P0(2)+t_top*(P1(2)-P0(2)) P0(3)+t_top*(P1(3)-P0(3))];

%% Calculate Beam Reflection from Top Mirror

beam_top_refl = -quatmultiply(quatmultiply([0 norm],([0 P0]-[0 P1])),[0 norm]);

%% Calculate Beam Line Intersection Point on Bottom Mirror
norm = bot_mirror_norm;
P0 = top_ints_pt;
P1 = top_ints_pt + beam_top_refl(2:4);
P2 = r_bot1_prime(2:4);

t_bot = (norm(1)*P0(1)-norm(1)*P2(1) + ...
            norm(2)*P0(2)-norm(2)*P2(2) + ...
                norm(3)*P0(3)-norm(3)*P2(3))/...
                    (norm(1)*P0(1)-norm(1)*P1(1)+...
                        norm(2)*P0(2)-norm(2)*P1(2)+...
                            norm(3)*P0(3)-norm(3)*P1(3));

bot_ints_pt = [P0(1)+t_bot*(P1(1)-P0(1)) P0(2)+t_bot*(P1(2)-P0(2)) P0(3)+t_bot*(P1(3)-P0(3))];

%% Calculate Beam Reflection from Bottom Mirror

beam_bot_refl = quatmultiply(quatmultiply([0 norm],([0 P0]-[0 P1])),[0 norm]);

%% Calculate Translation Compensation

if strcmp('PITCH',mode)
    trans_comp = abs(bot_ints_pt(3)) + abs(l_focus*sind(theta));
else
    trans_comp = abs(bot_ints_pt(1)) + abs(l_focus*sind(theta));
end

%% Translate Mirrors

if strcmp('PITCH',mode)
    if theta > 0
        r_iris1_comp = r_iris1_prime(2:4)+ [0 0 trans_comp];
        r_iris2_comp = r_iris2_prime(2:4)+ [0 0 trans_comp];
        r_iris3_comp = r_iris3_prime(2:4)+ [0 0 trans_comp];
        r_bot1_comp = r_bot1_prime(2:4)+ [0 0 trans_comp];
        r_bot2_comp = r_bot2_prime(2:4)+ [0 0 trans_comp];
        r_bot3_comp = r_bot3_prime(2:4)+ [0 0 trans_comp];
        r_top4_comp = r_top4_prime(2:4)+ [0 0 trans_comp];
        r_top5_comp = r_top5_prime(2:4)+ [0 0 trans_comp];
        r_top6_comp = r_top6_prime(2:4)+ [0 0 trans_comp];
        r_detc1_comp = r_detc1_prime(2:4)+ [0 0 trans_comp];
        r_detc2_comp = r_detc2_prime(2:4)+ [0 0 trans_comp];
        r_detc3_comp = r_detc3_prime(2:4)+ [0 0 trans_comp];
    else
        r_iris1_comp = r_iris1_prime(2:4)- [0 0 trans_comp];
        r_iris2_comp = r_iris2_prime(2:4)- [0 0 trans_comp];
        r_iris3_comp = r_iris3_prime(2:4)- [0 0 trans_comp];
        r_bot1_comp = r_bot1_prime(2:4)- [0 0 trans_comp];
        r_bot2_comp = r_bot2_prime(2:4)- [0 0 trans_comp];
        r_bot3_comp = r_bot3_prime(2:4)- [0 0 trans_comp];
        r_top4_comp = r_top4_prime(2:4)- [0 0 trans_comp];
        r_top5_comp = r_top5_prime(2:4)- [0 0 trans_comp];
        r_top6_comp = r_top6_prime(2:4)- [0 0 trans_comp];
        r_detc1_comp = r_detc1_prime(2:4)- [0 0 trans_comp];
        r_detc2_comp = r_detc2_prime(2:4)- [0 0 trans_comp];
        r_detc3_comp = r_detc3_prime(2:4)- [0 0 trans_comp];
    end
else
    if theta > 0
        r_iris1_comp = r_iris1_prime(2:4)- [trans_comp 0 0];
        r_iris2_comp = r_iris2_prime(2:4)- [trans_comp 0 0];
        r_iris3_comp = r_iris3_prime(2:4)- [trans_comp 0 0];
        r_bot1_comp = r_bot1_prime(2:4)- [trans_comp 0 0];
        r_bot2_comp = r_bot2_prime(2:4)- [trans_comp 0 0];
        r_bot3_comp = r_bot3_prime(2:4)- [trans_comp 0 0];
        r_top4_comp = r_top4_prime(2:4)- [trans_comp 0 0];
        r_top5_comp = r_top5_prime(2:4)- [trans_comp 0 0];
        r_top6_comp = r_top6_prime(2:4)- [trans_comp 0 0];
        r_detc1_comp = r_detc1_prime(2:4)- [trans_comp 0 0];
        r_detc2_comp = r_detc2_prime(2:4)- [trans_comp 0 0];
        r_detc3_comp = r_detc3_prime(2:4)- [trans_comp 0 0];
    else
        r_iris1_comp = r_iris1_prime(2:4)+ [trans_comp 0 0];
        r_iris2_comp = r_iris2_prime(2:4)+ [trans_comp 0 0];
        r_iris3_comp = r_iris3_prime(2:4)+ [trans_comp 0 0];
        r_bot1_comp = r_bot1_prime(2:4)+ [trans_comp 0 0];
        r_bot2_comp = r_bot2_prime(2:4)+ [trans_comp 0 0];
        r_bot3_comp = r_bot3_prime(2:4)+ [trans_comp 0 0];
        r_top4_comp = r_top4_prime(2:4)+ [trans_comp 0 0];
        r_top5_comp = r_top5_prime(2:4)+ [trans_comp 0 0];
        r_top6_comp = r_top6_prime(2:4)+ [trans_comp 0 0];
        r_detc1_comp = r_detc1_prime(2:4)+ [trans_comp 0 0];
        r_detc2_comp = r_detc2_prime(2:4)+ [trans_comp 0 0];
        r_detc3_comp = r_detc3_prime(2:4)+ [trans_comp 0 0];
    end
end
p1_comp = [r_iris1_comp;r_bot1_comp;r_top4_comp; r_detc1_comp];
p2_comp = [r_iris2_comp;r_bot2_comp;r_top5_comp; r_detc2_comp];
p3_comp = [r_iris3_comp;r_bot3_comp;r_top6_comp; r_detc3_comp];

[center_comp, rad_comp, v1_comp, v2_comp] = circlefit3d(p1_comp,p2_comp,p3_comp);


%% Plot Results
figure;hold on;
% Plot Origin
% plot3([origin(1) unitx(1)],[origin(2) unitx(2)],[origin(3) unitx(3)],'LineWidth',5);
% plot3([origin(1) unity(1)],[origin(2) unity(2)],[origin(3) unity(3)],'LineWidth',5);
% plot3([origin(1) unitz(1)],[origin(2) unitz(2)],[origin(3) unitz(3)],'LineWidth',5);
% Plot Beamline
plot3([beam1(2) top_ints_pt(1)],[beam1(3) top_ints_pt(2)],[beam1(4) top_ints_pt(3)],'LineWidth',5,'Color','g');
plot3([top_ints_pt(1) bot_ints_pt(1)],[top_ints_pt(2) bot_ints_pt(2)],[top_ints_pt(3) bot_ints_pt(3)],'LineWidth',5,'Color','g');
plot3([bot_ints_pt(1) (bot_ints_pt(1)+beam_bot_refl(2))],[bot_ints_pt(2) (bot_ints_pt(2)+beam_bot_refl(3))],[bot_ints_pt(3) (bot_ints_pt(3)+beam_bot_refl(4))],'LineWidth',5,'Color','g');
% Plot FOV
% plot3([origin(1) r_FOV1(2)],[origin(2) r_FOV1(3)],[origin(3) r_FOV1(4)],'LineWidth',2,'Color','b');
% plot3([origin(1) r_FOV1_prime(2)],[origin(2) r_FOV1_prime(3)],[origin(3) r_FOV1_prime(4)],'LineWidth',2,'Color','b');
% plot3([origin(1) r_FOV2(2)],[origin(2) r_FOV2(3)],[origin(3) r_FOV2(4)],'LineWidth',2,'Color','r');
% plot3([origin(1) r_FOV2_prime(2)],[origin(2) r_FOV2_prime(3)],[origin(3) r_FOV2_prime(4)],'LineWidth',2,'Color','r');
% plot3([origin(1) r_FOV3(2)],[origin(2) r_FOV3(3)],[origin(3) r_FOV3(4)],'LineWidth',2,'Color','g');
% plot3([origin(1) r_FOV3_prime(2)],[origin(2) r_FOV3_prime(3)],[origin(3) r_FOV3_prime(4)],'LineWidth',2,'Color','g');
% plot3([origin(1) r_FOV4(2)],[origin(2) r_FOV4(3)],[origin(3) r_FOV4(4)],'LineWidth',2,'Color','b');
% plot3([origin(1) r_FOV4_prime(2)],[origin(2) r_FOV4_prime(3)],[origin(3) r_FOV4_prime(4)],'LineWidth',2,'Color','b');
% plot3([origin(1) r_FOV5(2)],[origin(2) r_FOV5(3)],[origin(3) r_FOV5(4)],'LineWidth',2,'Color','r');
% plot3([origin(1) r_FOV5_prime(2)],[origin(2) r_FOV5_prime(3)],[origin(3) r_FOV5_prime(4)],'LineWidth',2,'Color','r');
% plot3([origin(1) r_FOV6(2)],[origin(2) r_FOV6(3)],[origin(3) r_FOV6(4)],'LineWidth',2,'Color','g');
% plot3([origin(1) r_FOV6_prime(2)],[origin(2) r_FOV6_prime(3)],[origin(3) r_FOV6_prime(4)],'LineWidth',2,'Color','g');
% Plot Mirror Normal Vector
plot3([r_bot2_prime(2) (r_bot2_prime(2)+bot_mirror_norm(1))],[r_bot2_prime(3) (r_bot2_prime(3)+bot_mirror_norm(2))],[r_bot2_prime(4) (r_bot2_prime(4)+bot_mirror_norm(3))],'LineWidth',3,'Color','c');
plot3([top_ints_pt(1) (top_ints_pt(1)+top_mirror_norm(1))],[top_ints_pt(2) (top_ints_pt(2)+top_mirror_norm(2))],[top_ints_pt(3) (top_ints_pt(3)+top_mirror_norm(3))],'LineWidth',3,'Color','c');

% Plot Mirrors and Iris
% Default (Boresight)
for i=1:1000
    a = i/180*pi;
    x = center(:,1)+sin(a)*rad.*v1(:,1)+cos(a)*rad.*v2(:,1);
    y = center(:,2)+sin(a)*rad.*v1(:,2)+cos(a)*rad.*v2(:,2);
    z = center(:,3)+sin(a)*rad.*v1(:,3)+cos(a)*rad.*v2(:,3);
    plot3(x,y,z,'k.');
end
% Rotated by Theta
for i=1:1000
    a = i/180*pi;
    x_prime = center_prime(:,1)+sin(a)*rad_prime.*v1_prime(:,1)+cos(a)*rad_prime.*v2_prime(:,1);
    y_prime = center_prime(:,2)+sin(a)*rad_prime.*v1_prime(:,2)+cos(a)*rad_prime.*v2_prime(:,2);
    z_prime = center_prime(:,3)+sin(a)*rad_prime.*v1_prime(:,3)+cos(a)*rad_prime.*v2_prime(:,3);
    plot3(x_prime,y_prime,z_prime,'r.');
end
% Translated for Compensation
for i=1:1000
    a = i/180*pi;
    x_comp = center_comp(:,1)+sin(a)*rad_comp.*v1_comp(:,1)+cos(a)*rad_comp.*v2_comp(:,1);
    y_comp = center_comp(:,2)+sin(a)*rad_comp.*v1_comp(:,2)+cos(a)*rad_comp.*v2_comp(:,2);
    z_comp = center_comp(:,3)+sin(a)*rad_comp.*v1_comp(:,3)+cos(a)*rad_comp.*v2_comp(:,3);
    plot3(x_comp,y_comp,z_comp,'b.');
end
grid on;
rotate3d on;
axis equal;
xlabel('X [mm]');
ylabel('Y [mm]');
zlabel('Z [mm]');
set(gca,'CameraPosition',[-40 80 50]);
