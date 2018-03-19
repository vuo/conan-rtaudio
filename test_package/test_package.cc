#include <stdio.h>
#include <RtAudio/RtAudio.h>

int main()
{
	RtAudio rta;
	unsigned int deviceCount = rta.getDeviceCount();
	for (unsigned int i = 0; i < deviceCount; ++i)
	{
		RtAudio::DeviceInfo info = rta.getDeviceInfo(i);
		printf("%s    %s\n", info.modelUid.c_str(), info.name.c_str());
	}
	return 0;
}
