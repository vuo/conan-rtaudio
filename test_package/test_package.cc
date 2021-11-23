#include <stdio.h>
#include <RtAudio/RtAudio.h>

int main()
{
	printf("RtAudio version %s\n", RtAudio::getVersion().c_str());
	RtAudio rta;
	unsigned int deviceCount = rta.getDeviceCount();
	printf("%u devices:\n", deviceCount);
	for (unsigned int i = 0; i < deviceCount; ++i)
	{
		RtAudio::DeviceInfo info = rta.getDeviceInfo(i);
		printf("    \"%s\":\n", info.name.c_str());
		printf("        modelUid=%s\n", info.modelUid.c_str());
		if (info.inputChannels)
		printf("        inputs=%d\n", info.inputChannels);
		if (info.outputChannels)
		printf("        outputs=%d\n", info.outputChannels);
		printf("        sample rates:\n");
		for (unsigned int sr : info.sampleRates)
			printf("            %u%s\n", sr, sr == info.preferredSampleRate ? " (preferred)" : "");
	}
	return 0;
}
