# **SDK Example**

## runtime

### axcl\_sample\_runtime

Example of calling Runtime API.

**1\. Initialize the runtime via \`axclInit\`.**  
**2\. Activate the device via \`axclrtSetDevice\`.**  
**3\. Create a context for the main thread via \`axclrtCreateDevice\` (optional).**  
**4\. Create and destroy thread contexts (required).**  
**5\. Destroy the context of the main thread.**  
**6\. Deactivate the device via \`axclrtResetDevice\`.**  
**7\. Deinitialize the runtime via \`axclFinalize\`.**

#### Usage

**m5stack@raspberrypi5:\~ $ axcl\_sample\_runtime \--help**  
**\[INFO \]\[                            main\]\[  36\]: \============== V3.6.3\_20250722020142 sample started Jul 22 2025 02:31:26 \=============**  
**usage: axcl\_sample\_runtime \[options\] ...**  
**options:**  
  **\-d, \--device    device index \[-1, connected device num \- 1\], \-1: traverse all devices (int \[=-1\])**  
      **\--json      axcl.json path (string \[=./axcl.json\])**  
      **\--reboot    reboot device**  
  **\-?, \--help      print this message**

| Parameter | Default Value | Description |
| :---: | :---: | :---: |
| \-d, \--device | \-1, range: \[-1, 0 \- connected device num \- 1\] | Specify the device index. \-1: traverse all devices |
| \--json | [axcl.json](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_samples#faq_axcl_json) | file path |
| \--reboot | NA | Make the device panic and reboot. |

#### Example 1

Query the properties of device \#0.

**m5stack@raspberrypi5:\~ $ axcl\_sample\_runtime \-d 0**  
**\[INFO \]\[                            main\]\[  36\]: \============== V3.6.3\_20250722020142 sample started Jul 22 2025 02:31:26 \=============**  
**json file**  
**\[INFO \]\[                      operator()\]\[ 130\]: \[0001:01.0\] software version: Ax\_Version V3.6.3\_20250722020142**

**\[INFO \]\[                      operator()\]\[ 131\]: \[0001:01.0\] uid             : 0x600408144b65d204**  
**\[INFO \]\[                      operator()\]\[ 132\]: \[0001:01.0\] temperature     : 49263**  
**\[INFO \]\[                      operator()\]\[ 133\]: \[0001:01.0\] total mem size  : 968356   KB**  
**\[INFO \]\[                      operator()\]\[ 134\]: \[0001:01.0\] free  mem size  : 815084   KB**  
**\[INFO \]\[                      operator()\]\[ 135\]: \[0001:01.0\] total cmm size  : 7208960  KB**  
**\[INFO \]\[                      operator()\]\[ 136\]: \[0001:01.0\] free  cmm size  : 7190084  KB**  
**\[INFO \]\[                      operator()\]\[ 137\]: \[0001:01.0\] avg cpu loading : 0.0%**  
**\[INFO \]\[                      operator()\]\[ 138\]: \[0001:01.0\] avg npu loading : 0.0%**  
**\[INFO \]\[                      operator()\]\[ 149\]: malloc 1048576 bytes memory from device  1 success, addr \= 0x14926f000**  
**\[INFO \]\[                            main\]\[ 215\]: \============== V3.6.3\_20250722020142 sample exited Jul 22 2025 02:31:26 \==============**

#### Example 2

Manually make device \#0 panic by sending **echo c \> /proc/sysrq-trigger**, then reboot and download the firmware again.

**m5stack@raspberrypi5:\~ $ axcl\_sample\_runtime \-d 0 \--reboot**  
**\[INFO \]\[                            main\]\[  36\]: \============== V3.6.3\_20250722020142 sample started Jul 22 2025 02:31:26 \=============**  
**json file**  
**\[INFO \]\[                      operator()\]\[ 130\]: \[0001:01.0\] software version: Ax\_Version V3.6.3\_20250722020142**

**\[INFO \]\[                      operator()\]\[ 131\]: \[0001:01.0\] uid             : 0x600408144b65d204**  
**\[INFO \]\[                      operator()\]\[ 132\]: \[0001:01.0\] temperature     : 49263**  
**\[INFO \]\[                      operator()\]\[ 133\]: \[0001:01.0\] total mem size  : 968356   KB**  
**\[INFO \]\[                      operator()\]\[ 134\]: \[0001:01.0\] free  mem size  : 814888   KB**  
**\[INFO \]\[                      operator()\]\[ 135\]: \[0001:01.0\] total cmm size  : 7208960  KB**  
**\[INFO \]\[                      operator()\]\[ 136\]: \[0001:01.0\] free  cmm size  : 7190084  KB**  
**\[INFO \]\[                      operator()\]\[ 137\]: \[0001:01.0\] avg cpu loading : 1.2%**  
**\[INFO \]\[                      operator()\]\[ 138\]: \[0001:01.0\] avg npu loading : 0.0%**  
**\[INFO \]\[                      operator()\]\[ 149\]: malloc 1048576 bytes memory from device  1 success, addr \= 0x14926f000**  
**\[INFO \]\[                            main\]\[ 178\]: panic device 0x1**  
**\[INFO \]\[                            main\]\[ 185\]: wait for device 0x1 to reboot in 60 seconds**  
**\[FAIL \]\[                            main\]\[ 203\]: device 0x1 reboot timeout**  
**\[INFO \]\[                            main\]\[ 215\]: \============== V3.6.3\_20250722020142 sample exited Jul 22 2025 02:31:26 \==============**

### axcl\_sample\_memory

Example of memory copy between HOST and DEVICE.

        **HOST          |               DEVICE**  
      **host\_mem\[0\] \-----------\> dev\_mem\[0\]**  
                                    **|---------\> dev\_mem\[1\]**  
      **host\_mem\[1\] \<----------------------------------|**

**1\. Allocate host\_mem\[2\] by \`axclrtMallocHost\` and dev\_mem\[2\] by \`axclrtMalloc\`.**  
**2\. axclrtMemcpy(dev\_mem\[0\], host\_mem\[0\], size, AXCL\_MEMCPY\_HOST\_TO\_DEVICE)**  
**3\. axclrtMemcpy(dev\_mem\[1\], dev\_mem\[0\], size, AXCL\_MEMCPY\_DEVICE\_TO\_DEVICE)**  
**4\. axclrtMemcpy(host\_mem\[1\], dev\_mem\[1\], size, AXCL\_MEMCPY\_DEVICE\_TO\_HOST)**  
**5\. memcmp(host\_mem\[0\], host\_mem\[1\], size)**

#### Usage

**m5stack@raspberrypi5:\~ $ axcl\_sample\_memory \--help**  
**\[INFO \]\[                            main\]\[  32\]: \============== V3.6.3\_20250722020142 sample started Jul 22 2025 02:31:27 \==============**

**usage: axcl\_sample\_memory \[options\] ...**  
**options:**  
  **\-d, \--device    device index from 0 to connected device num \- 1 (int \[=0\])**  
      **\--json      axcl.json path (string \[=./axcl.json\])**  
  **\-?, \--help      print this message**

| Parameter | Default Value | Description |
| :---: | :---: | :---: |
| \-d, \--device | 0, range: \[0 \- connected device num \-1\] | Specify the device index |
| \--json | [axcl.json](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_samples#faq_axcl_json) | file path |

#### Example

**m5stack@raspberrypi5:\~ $ axcl\_sample\_memory  \-d 0**  
**\[INFO \]\[                            main\]\[  32\]: \============== V3.6.3\_20250722020142 sample started Jul 22 2025 02:31:27 \==============**

**\[INFO \]\[                           setup\]\[ 112\]: json: ./axcl.json**  
**json file**  
**\[INFO \]\[                           setup\]\[ 131\]: device index: 0, bus number: 1**  
**\[INFO \]\[                            main\]\[  51\]: alloc host and device memory, size: 0x800000**  
**\[INFO \]\[                            main\]\[  63\]: memory \[0\]: host 0x7fff277fc010, device 0x14926f000**  
**\[INFO \]\[                            main\]\[  63\]: memory \[1\]: host 0x7fff26ff8010, device 0x149a6f000**  
**\[INFO \]\[                            main\]\[  69\]: memcpy from host memory\[0\] 0x7fff277fc010 to device memory\[0\] 0x14926f000**  
**\[INFO \]\[                            main\]\[  75\]: memcpy device memory\[0\] 0x14926f000 to device memory\[1\] 0x149a6f000**  
**\[INFO \]\[                            main\]\[  81\]: memcpy device memory\[1\] 0x149a6f000 to host memory\[0\] 0x7fff26ff8010**  
**\[INFO \]\[                            main\]\[  88\]: compare host memory\[0\] 0x7fff277fc010 and host memory\[1\] 0x7fff26ff8010 success**  
**\[INFO \]\[                         cleanup\]\[ 146\]: deactive device 1 and cleanup axcl**  
**\[INFO \]\[                            main\]\[ 106\]: \============== V3.6.3\_20250722020142 sample exited Jul 22 2025 02:31:27 \==============**

## native

### axcl\_sample\_sys

* Example usage of the native SYS module, including:  
* Allocation and release of non-cached CMM memory.  
* Allocation and release of cached CMM memory.  
* Allocation and release from a general memory pool.  
* Allocation and release from a private memory pool.  
* Module linking and query.

#### Usage

**m5stack@raspberrypi5:\~ $ axcl\_sample\_sys \--help**  
**usage: axcl\_sample\_sys \[options\] ...**  
**options:**  
  **\-d, \--device    device index from 0 to connected device num \- 1 (unsigned int \[=0\])**  
      **\--json      axcl.json path (string \[=./axcl.json\])**  
  **\-?, \--help      print this message**

| Parameter | Default Value | Description |
| :---: | :---: | :---: |
| \-d, \--device | 0, range: \[0 \- connected device num \-1\] | Specify the device index |
| \--json | [axcl.json](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_samples#faq_axcl_json) | file path |

#### Example

**m5stack@raspberrypi5:\~ $ axcl\_sample\_sys \-d 0**  
**\[INFO \]\[                            main\]\[  35\]: json: ./axcl.json**  
**json file**  
**\[INFO \]\[                            main\]\[  55\]: device index: 0, bus number: 1**  
**\[INFO \]\[           sample\_sys\_alloc\_free\]\[  82\]: sys\_alloc\_free begin**  
**\[INFO \]\[           sample\_sys\_alloc\_free\]\[  91\]: alloc PhyAddr= 0x14926f000,pVirAddr=0xffffafafe000**  
**\[INFO \]\[           sample\_sys\_alloc\_free\]\[  91\]: alloc PhyAddr= 0x14936f000,pVirAddr=0xffffaf9fe000**  
**\[INFO \]\[           sample\_sys\_alloc\_free\]\[  91\]: alloc PhyAddr= 0x14946f000,pVirAddr=0xffffaf8fe000**  
**\[INFO \]\[           sample\_sys\_alloc\_free\]\[  91\]: alloc PhyAddr= 0x14956f000,pVirAddr=0xffffaf7fe000**  
**\[INFO \]\[           sample\_sys\_alloc\_free\]\[  91\]: alloc PhyAddr= 0x14966f000,pVirAddr=0xffffaf6fe000**  
**\[INFO \]\[           sample\_sys\_alloc\_free\]\[  91\]: alloc PhyAddr= 0x14976f000,pVirAddr=0xffffaf5fe000**  
**\[INFO \]\[           sample\_sys\_alloc\_free\]\[  91\]: alloc PhyAddr= 0x14986f000,pVirAddr=0xffffaf4fe000**  
**\[INFO \]\[           sample\_sys\_alloc\_free\]\[  91\]: alloc PhyAddr= 0x14996f000,pVirAddr=0xffffaf3fe000**  
**\[INFO \]\[           sample\_sys\_alloc\_free\]\[  91\]: alloc PhyAddr= 0x149a6f000,pVirAddr=0xffffaf2fe000**  
**\[INFO \]\[           sample\_sys\_alloc\_free\]\[  91\]: alloc PhyAddr= 0x149b6f000,pVirAddr=0xffffaf1fe000**  
**\[INFO \]\[           sample\_sys\_alloc\_free\]\[ 100\]: free PhyAddr= 0x14926f000,pVirAddr=0xffffafafe000**  
**\[INFO \]\[           sample\_sys\_alloc\_free\]\[ 100\]: free PhyAddr= 0x14936f000,pVirAddr=0xffffaf9fe000**  
**\[INFO \]\[           sample\_sys\_alloc\_free\]\[ 100\]: free PhyAddr= 0x14946f000,pVirAddr=0xffffaf8fe000**  
**\[INFO \]\[           sample\_sys\_alloc\_free\]\[ 100\]: free PhyAddr= 0x14956f000,pVirAddr=0xffffaf7fe000**  
**\[INFO \]\[           sample\_sys\_alloc\_free\]\[ 100\]: free PhyAddr= 0x14966f000,pVirAddr=0xffffaf6fe000**  
**\[INFO \]\[           sample\_sys\_alloc\_free\]\[ 100\]: free PhyAddr= 0x14976f000,pVirAddr=0xffffaf5fe000**  
**\[INFO \]\[           sample\_sys\_alloc\_free\]\[ 100\]: free PhyAddr= 0x14986f000,pVirAddr=0xffffaf4fe000**  
**\[INFO \]\[           sample\_sys\_alloc\_free\]\[ 100\]: free PhyAddr= 0x14996f000,pVirAddr=0xffffaf3fe000**  
**\[INFO \]\[           sample\_sys\_alloc\_free\]\[ 100\]: free PhyAddr= 0x149a6f000,pVirAddr=0xffffaf2fe000**  
**\[INFO \]\[           sample\_sys\_alloc\_free\]\[ 100\]: free PhyAddr= 0x149b6f000,pVirAddr=0xffffaf1fe000**  
**\[INFO \]\[           sample\_sys\_alloc\_free\]\[ 103\]: sys\_alloc\_free end success**  
**\[INFO \]\[     sample\_sys\_alloc\_cache\_free\]\[ 115\]: sys\_alloc\_cache\_free begin**  
**\[INFO \]\[     sample\_sys\_alloc\_cache\_free\]\[ 124\]: alloc PhyAddr= 0x14926f000,pVirAddr=0xffffafafe000**  
**\[INFO \]\[     sample\_sys\_alloc\_cache\_free\]\[ 124\]: alloc PhyAddr= 0x14936f000,pVirAddr=0xffffaf9fe000**  
**\[INFO \]\[     sample\_sys\_alloc\_cache\_free\]\[ 124\]: alloc PhyAddr= 0x14946f000,pVirAddr=0xffffaf8fe000**  
**\[INFO \]\[     sample\_sys\_alloc\_cache\_free\]\[ 124\]: alloc PhyAddr= 0x14956f000,pVirAddr=0xffffaf7fe000**  
**\[INFO \]\[     sample\_sys\_alloc\_cache\_free\]\[ 124\]: alloc PhyAddr= 0x14966f000,pVirAddr=0xffffaf6fe000**  
**\[INFO \]\[     sample\_sys\_alloc\_cache\_free\]\[ 124\]: alloc PhyAddr= 0x14976f000,pVirAddr=0xffffaf5fe000**  
**\[INFO \]\[     sample\_sys\_alloc\_cache\_free\]\[ 124\]: alloc PhyAddr= 0x14986f000,pVirAddr=0xffffaf4fe000**  
**\[INFO \]\[     sample\_sys\_alloc\_cache\_free\]\[ 124\]: alloc PhyAddr= 0x14996f000,pVirAddr=0xffffaf3fe000**  
**\[INFO \]\[     sample\_sys\_alloc\_cache\_free\]\[ 124\]: alloc PhyAddr= 0x149a6f000,pVirAddr=0xffffaf2fe000**  
**\[INFO \]\[     sample\_sys\_alloc\_cache\_free\]\[ 124\]: alloc PhyAddr= 0x149b6f000,pVirAddr=0xffffaf1fe000**  
**\[INFO \]\[     sample\_sys\_alloc\_cache\_free\]\[ 133\]: free PhyAddr= 0x14926f000,pVirAddr=0xffffafafe000**  
**\[INFO \]\[     sample\_sys\_alloc\_cache\_free\]\[ 133\]: free PhyAddr= 0x14936f000,pVirAddr=0xffffaf9fe000**  
**\[INFO \]\[     sample\_sys\_alloc\_cache\_free\]\[ 133\]: free PhyAddr= 0x14946f000,pVirAddr=0xffffaf8fe000**  
**\[INFO \]\[     sample\_sys\_alloc\_cache\_free\]\[ 133\]: free PhyAddr= 0x14956f000,pVirAddr=0xffffaf7fe000**  
**\[INFO \]\[     sample\_sys\_alloc\_cache\_free\]\[ 133\]: free PhyAddr= 0x14966f000,pVirAddr=0xffffaf6fe000**  
**\[INFO \]\[     sample\_sys\_alloc\_cache\_free\]\[ 133\]: free PhyAddr= 0x14976f000,pVirAddr=0xffffaf5fe000**  
**\[INFO \]\[     sample\_sys\_alloc\_cache\_free\]\[ 133\]: free PhyAddr= 0x14986f000,pVirAddr=0xffffaf4fe000**  
**\[INFO \]\[     sample\_sys\_alloc\_cache\_free\]\[ 133\]: free PhyAddr= 0x14996f000,pVirAddr=0xffffaf3fe000**  
**\[INFO \]\[     sample\_sys\_alloc\_cache\_free\]\[ 133\]: free PhyAddr= 0x149a6f000,pVirAddr=0xffffaf2fe000**  
**\[INFO \]\[     sample\_sys\_alloc\_cache\_free\]\[ 133\]: free PhyAddr= 0x149b6f000,pVirAddr=0xffffaf1fe000**  
**\[INFO \]\[     sample\_sys\_alloc\_cache\_free\]\[ 136\]: sys\_alloc\_cache\_free end success**  
**\[INFO \]\[          sample\_sys\_commom\_pool\]\[ 148\]: sys\_commom\_pool begin**  
**\[INFO \]\[          sample\_sys\_commom\_pool\]\[ 157\]: AXCL\_SYS\_Init success\!**  
**\[INFO \]\[          sample\_sys\_commom\_pool\]\[ 167\]: AXCL\_POOL\_Exit success\!**  
**\[INFO \]\[          sample\_sys\_commom\_pool\]\[ 199\]: AXCL\_POOL\_SetConfig success\!**  
**\[INFO \]\[          sample\_sys\_commom\_pool\]\[ 208\]: AXCL\_POOL\_Init success\!**  
**\[INFO \]\[          sample\_sys\_commom\_pool\]\[ 222\]: AXCL\_POOL\_GetBlock success\!BlkId:0x5E002000**  
**\[INFO \]\[          sample\_sys\_commom\_pool\]\[ 233\]: AXCL\_POOL\_Handle2PoolId success\!(Blockid:0x5E002000 \--\> PoolId=2)**  
**\[INFO \]\[          sample\_sys\_commom\_pool\]\[ 244\]: AXCL\_POOL\_Handle2PhysAddr success\!(Blockid:0x5E002000 \--\> PhyAddr=0x14ad8d000)**  
**\[INFO \]\[          sample\_sys\_commom\_pool\]\[ 255\]: AXCL\_POOL\_Handle2MetaPhysAddr success\!(Blockid:0x5E002000 \--\> MetaPhyAddr=0x14a18b000)**  
**\[INFO \]\[          sample\_sys\_commom\_pool\]\[ 265\]: AXCL\_POOL\_ReleaseBlock success\!Blockid=0x5e002000**  
**\[INFO \]\[          sample\_sys\_commom\_pool\]\[ 275\]: AXCL\_POOL\_Exit success\!**  
**\[INFO \]\[          sample\_sys\_commom\_pool\]\[ 285\]: AXCL\_SYS\_Deinit success\!**  
**\[INFO \]\[          sample\_sys\_commom\_pool\]\[ 288\]: sys\_commom\_pool end success\!**  
**\[INFO \]\[         sample\_sys\_private\_pool\]\[ 310\]: sys\_private\_pool begin**  
**\[INFO \]\[         sample\_sys\_private\_pool\]\[ 319\]: AXCL\_SYS\_Init success\!**  
**\[INFO \]\[         sample\_sys\_private\_pool\]\[ 329\]: AXCL\_POOL\_Exit success\!**  
**\[INFO \]\[         sample\_sys\_private\_pool\]\[ 349\]: AXCL\_POOL\_CreatePool\[0\] success**  
**\[INFO \]\[         sample\_sys\_private\_pool\]\[ 367\]: AXCL\_POOL\_CreatePool\[1\] success**  
**\[INFO \]\[         sample\_sys\_private\_pool\]\[ 378\]: AXCL\_POOL\_GetBlock success\!BlkId:0x5E001000**  
**\[INFO \]\[         sample\_sys\_private\_pool\]\[ 389\]: AXCL\_POOL\_Handle2PoolId success\!(Blockid:0x5E001000 \--\> PoolId=1)**  
**\[INFO \]\[         sample\_sys\_private\_pool\]\[ 400\]: AX\_POOL\_Handle2PhysAddr success\!(Blockid:0x5E001000 \--\> PhyAddr=0x149879000)**  
**\[INFO \]\[         sample\_sys\_private\_pool\]\[ 411\]: AXCL\_POOL\_Handle2MetaPhysAddr success\!(Blockid:0x5E001000 \--\> MetaPhyAddr=0x149477000)**  
**\[INFO \]\[         sample\_sys\_private\_pool\]\[ 421\]: AXCL\_POOL\_ReleaseBlock success\!Blockid=0x5e001000**  
**\[INFO \]\[         sample\_sys\_private\_pool\]\[ 430\]: AXCL\_POOL\_DestroyPool\[1\] success\!**  
**\[INFO \]\[         sample\_sys\_private\_pool\]\[ 438\]: AXCL\_POOL\_DestroyPool\[0\] success\!**  
**\[INFO \]\[         sample\_sys\_private\_pool\]\[ 448\]: AXCL\_SYS\_Deinit success\!**  
**\[INFO \]\[         sample\_sys\_private\_pool\]\[ 451\]: sys\_private\_pool end success\!**  
**\[INFO \]\[                 sample\_sys\_link\]\[ 472\]: sample\_sys\_link begin**  
**\[INFO \]\[                 sample\_sys\_link\]\[ 487\]: AXCL\_SYS\_Init success\!**  
**\[INFO \]\[                 sample\_sys\_link\]\[ 554\]: AXCL\_SYS\_Deinit success\!**  
**\[INFO \]\[                 sample\_sys\_link\]\[ 557\]: sample\_sys\_link end success\!**

### axcl\_sample\_vdec

Example of H264 and H265 Video Decoder (VDEC).

1. Load .mp4 file or .h264/.h265 raw bitstream file.  
2. Demux nalu frames via ffmpeg.  
3. Send nalus to the video decoder frame by frame.  
4. Receive decoded nv12 image information.

#### Usage

**m5stack@raspberrypi5:\~ $ axcl\_sample\_vdec \--help**  
**\[INFO \]\[                            main\]\[  43\]: \============== V3.6.3\_20250722020142 sample started Jul 22 2025 02:31:31 \==============**

**usage: axcl\_sample\_vdec \--url=string \[options\] ...**  
**options:**  
  **\-i, \--url       mp4|.264|.265 file path (string)**  
  **\-d, \--device    device index from 0 to connected device num \- 1 (unsigned int \[=0\])**  
      **\--count     grp count (int \[=1\])**  
      **\--json      axcl.json path (string \[=./axcl.json\])**  
  **\-w, \--width     frame width (int \[=1920\])**  
  **\-h, \--height    frame height (int \[=1080\])**  
      **\--VdChn     channel id (int \[=0\])**  
      **\--yuv       transfer nv12 from device (int \[=0\])**  
  **\-?, \--help      print this message**

| Parameter | Default Value | Description |
| :---: | :---: | :---: |
| \-d, \--device | 0, range: \[0 \- connected device num \-1\] | Specify the device index. |
| \--json | [axcl.json](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_samples#faq_axcl_json) | file path |
| \-i, \--url | NA | Specify the path of the stream file. |
| \--count | 1 | Specify the number of groups. |
| \-w, \--width | 1920 | Specify the width of the decoded YUV image. |
| \-h, \--height | 1080 | Specify the height of the decoded YUV image. |
| \--VdChn | 0 | Specify the VDEC channel. 0: Outputs the original width and height of the input stream. 1: Output range \[48x48, 4096x4096\], supports width/height scaling. 2: Output range \[48x48, 1920x1080\], supports width/height scaling. |
| \--yuv | 0 | 1: Transfer decoded YUV image from device. 0: Do not transfer image. |

**Note:**

If you encounter the following error:

**$ axcl\_sample\_vdec \--help**  
**axcl\_sample\_vdec: error while loading shared libraries: libavcodec.so.61: cannot open shared object file: No such file or directory**  
Please set the environment variables first using the following command:

**$ export LD\_LIBRARY\_PATH=/usr/lib/axcl/ffmpeg:$LD\_LIBRARY\_PATH**

#### Example

**m5stack@raspberrypi5:\~ $ axcl\_sample\_vdec \-i input.mp4 \-d 0**  
**\[INFO \]\[                            main\]\[  43\]: \============== V3.6.3\_20250722020142 sample started Jul 22 2025 02:31:31 \==============**

**\[INFO \]\[                            main\]\[  68\]: json: ./axcl.json**  
**json file**  
**\[INFO \]\[                            main\]\[  88\]: device index: 0, bus number: 1**  
**\[INFO \]\[             ffmpeg\_init\_demuxer\]\[ 439\]: \[0\] url: input.mp4**  
**\[INFO \]\[             ffmpeg\_init\_demuxer\]\[ 502\]: \[0\] url input.mp4: codec 96, 1280x688, fps 30**  
**\[INFO \]\[                            main\]\[ 116\]: init sys**  
**\[INFO \]\[                            main\]\[ 125\]: init vdec**  
**\[INFO \]\[                            main\]\[ 139\]: start decoder 0**  
**\[INFO \]\[sample\_get\_vdec\_attr\_from\_stream\_info\]\[ 252\]: stream info: 1280x688 payload 96 fps 30**  
**\[INFO \]\[ sample\_get\_decoded\_image\_thread\]\[ 311\]: \[decoder  0\] decode thread \+++**  
**\[INFO \]\[                            main\]\[ 176\]: start demuxer 0**  
**\[INFO \]\[          ffmpeg\_dispatch\_thread\]\[ 189\]: \[0\] \+++**  
**\[INFO \]\[             ffmpeg\_demux\_thread\]\[ 295\]: \[0\] \+++**  
**\[INFO \]\[             ffmpeg\_demux\_thread\]\[ 328\]: \[0\] reach eof**  
**\[INFO \]\[             ffmpeg\_demux\_thread\]\[ 435\]: \[0\] demuxed    total 281 frames \---**  
**\[INFO \]\[          ffmpeg\_dispatch\_thread\]\[ 272\]: \[0\] dispatched total 281 frames \---**  
**\[WARN \]\[ sample\_get\_decoded\_image\_thread\]\[ 357\]: \[decoder  0\] flow end**  
**\[INFO \]\[ sample\_get\_decoded\_image\_thread\]\[ 392\]: \[decoder  0\] total decode 281 frames**  
**\[INFO \]\[ sample\_get\_decoded\_image\_thread\]\[ 398\]: \[decoder  0\] dfecode thread \---**  
**\[INFO \]\[                            main\]\[ 197\]: stop decoder 0**  
**\[INFO \]\[                            main\]\[ 202\]: decoder 0 is eof**  
**\[INFO \]\[                            main\]\[ 227\]: stop demuxer 0**  
**\[INFO \]\[                            main\]\[ 235\]: deinit vdec**  
**\[INFO \]\[                            main\]\[ 239\]: deinit sys**  
**\[INFO \]\[                            main\]\[ 243\]: axcl deinit**  
**\[INFO \]\[                            main\]\[ 247\]: \============== V3.6.3\_20250722020142 sample exited Jul 22 2025 02:31:31 \==============**

### axcl\_sample\_venc

Examples of H264, H265, JPEG, and MJPEG Encoders (VENC).

#### Usage

**m5stack@raspberrypi5:\~ $ axcl\_sample\_venc \--help**  
**\[INFO\]\[SAMPLE-VENC\]\[main\]\[39\]: Build at Jul 22 2025 02:31:34**

**Usage:  axcl\_sample\_venc \[options\] \-i input file**

  **\-H \--help                        help information**

**\#\# Options for sample**

  **\-i\[s\] \--input                         Read input video sequence from file. \[input.yuv\]**  
  **\-o\[s\] \--output                        Write output HEVC/H.264/jpeg/mjpeg stream to file.\[stream.hevc\]**  
  **\-W\[n\] \--write                         whether write output stream to file.\[1\]**  
                                        **0: do not write**  
                                        **1: write**

  **\-f\[n\] \--dstFrameRate                  1..1048575 Output picture rate numerator. \[30\]**

  **\-j\[n\] \--srcFrameRate                  1..1048575 Input picture rate numerator. \[30\]**

  **\-n\[n\] \--encFrameNum                   the frame number want to encode. \[0\]**  
  **\-N\[n\] \--chnNum                        total encode channel number. \[0\]**  
  **\-t\[n\] \--encThdNum                     total encode thread number. \[1\]**  
  **\-p\[n\] \--bLoopEncode                   enable loop mode to encode. 0: disable. 1: enable. \[0\]**  
  **\--codecType                           encoding payload type. \[0\]**  
                                        **0 \- SAMPLE\_CODEC\_H264**  
                                        **1 \- SAMPLE\_CODEC\_H265**  
                                        **2 \- SAMPLE\_CODEC\_MJPEG**  
                                        **3 \- SAMPLE\_CODEC\_JPEG**  
  **\--bChnCustom                          whether encode all payload type. \[0\]**  
                                        **0 \- encode all payload type**  
                                        **1 \- encode payload type codecType specified by codecType.**  
  **\--log                                 log info level. \[2\]**  
                                        **0 : ERR**  
                                        **1 : WARN**  
                                        **2 : INFO**  
                                        **3 : DEBUG**  
  **\--json                                axcl.json path**  
  **\--devId                               device index from 0 to connected device num \- 1\. \[0\]**

  **\--bStrmCached                         output stream use cached memory. \[0\]**  
  **\--bAttachHdr                          support attach headers(sps/pps) to PB frame for h.265. \[0\]**

**\#\# Parameters affecting input frame and encoded frame resolutions and cropping:**

  **\-w\[n\] \--picW                          Width of input image in pixels.**  
  **\-h\[n\] \--picH                          Height of input image in pixels.**

  **\-X\[n\] \--cropX                         image horizontal cropping offset, must be even. \[0\]**  
  **\-Y\[n\] \--cropY                         image vertical cropping offset, must be even. \[0\]**  
  **\-x\[n\] \--cropW                         Height of encoded image**  
  **\-y\[n\] \--cropH                         Width of encoded image**

  **\--maxPicW                             max width of input image in pixels.**  
  **\--maxPicH                             max height of input image in pixels.**

  **\--bCrop                               enable crop encode, 0: disable 1: enable crop. \[0\]**

**\#\# Parameters picture stride:**

  **\--strideY                             y stride**  
  **\--strideU                             u stride**  
  **\--strideV                             v stride**

**\#\# Parameters  for pre-processing frames before encoding:**

  **\-l\[n\] \--picFormat                     Input YUV format. \[1\]**  
                                        **1 \- AX\_FORMAT\_YUV420\_PLANAR (IYUV/I420)**  
                                        **3 \- AX\_FORMAT\_YUV420\_SEMIPLANAR (NV12)**  
                                        **4 \- AX\_FORMAT\_YUV420\_SEMIPLANAR\_VU (NV21)**  
                                        **13 \- AX\_FORMAT\_YUV422\_INTERLEAVED\_YUYV (YUYV/YUY2)**  
                                        **14 \- AX\_FORMAT\_YUV422\_INTERLEAVED\_UYVY (UYVY/Y422)**  
                                        **37 \- AX\_FORMAT\_YUV420\_PLANAR\_10BIT\_I010**  
                                        **42 \- AX\_FORMAT\_YUV420\_SEMIPLANAR\_10BIT\_P010**

**\#\# Parameters  affecting GOP pattern, rate control and output stream bitrate:**

  **\-g\[n\] \--gopLen                        Intra-picture rate in frames. \[30\]**  
                                        **Forces every Nth frame to be encoded as intra frame.**  
                                        **0 \= Do not force**

  **\-B\[n\] \--bitRate                       target bitrate for rate control, in kbps. \[2000\]**  
  **\--ltMaxBt                             the long-term target max bitrate.**  
  **\--ltMinBt                             the long-term target min bitrate.**  
  **\--ltStaTime                           the long-term rate statistic time.**  
  **\--shtStaTime                          the short-term rate statistic time.**  
  **\--minQpDelta                          Difference between FrameLevelMinQp and MinQp**  
  **\--maxQpDelta                          Difference between FrameLevelMaxQp and MaxQp**

**\#\# Parameters  qp:**

  **\-q\[n\] \--qFactor                       0..99, Initial target QP of jenc. \[90\]**  
  **\-b\[n\] \--bDblkEnable                   0: disable Deblock 1: enable Deblock. \[0\]**  
  **\--startQp                             \-1..51, start qp for first frame. \[16\]**  
  **\--vq                                  0..9 video quality level for vbr, def 0, min/max qp is invalid when vq \!= 0**  
  **\--minQp                               0..51, Minimum frame header qp for any picture. \[16\]**  
  **\--maxQp                               0..51, Maximum frame header qp for any picture. \[51\]**  
  **\--minIqp                              0..51, Minimum frame header qp for I picture. \[16\]**  
  **\--maxIqp                              0..51, Maximum frame header qp for I picture. \[51\]**  
  **\--chgPos                              vbr/avbr chgpos 20-100, def 90**  
  **\--stillPercent                        avbr still percent 10-100 def 25**  
  **\--stillQp                             0..51, the max QP value of I frame for still scene. \[0\]**

  **\--deltaQpI                            \-51..51, QP adjustment for intra frames. \[-2\]**  
  **\--maxIprop                            1..100, the max I P size ratio. \[100\]**  
  **\--minIprop                            1..maxIprop, the min I P size ratio. \[1\]**  
  **\--IQp                                 0..51, qp of the i frame. \[25\]**  
  **\--PQp                                 0..51, qp of the p frame. \[30\]**  
  **\--BQp                                 0..51, qp of the b frame. \[32\]**  
  **\--fixedQp                             \-1..51, Fixed qp for every frame(only for Mjpeg)**  
                                          **\-1 : disable fixed qp mode.**  
                                          **\[0, 51\] : value of fixed qp.**

  **\--ctbRcMode                           0: diable ctbRc; 1: quality first; 2: bitrate first 3: quality and bitrate balance**  
  **\--qpMapQpType                         0: disable qpmap; 1: deltaQp; 2: absQp**  
  **\--qpMapBlkUnit                        0: 64x64, 1: 32x32, 2: 16x16;**  
  **\--qpMapBlkType                        0: disable; 1: skip mode; 2: Ipcm mode**

  **\-r\[n\] \--rcMode                        0: CBR 1: VBR 2: AVBR 3: QPMAP 4:FIXQP 5:CVBR. \[0\]**

  **\-M\[n\] \--gopMode                       gopmode. 0: normalP. 1: oneLTR. 2: svc-t. \[0\]**

**\#\# other:**

  **\--vbCnt                               total frame buffer number of pool \[1, 100\]. \[10\]**  
  **\--inFifoDep                           input fifo depth. \[4\]**  
  **\--outFifoDep                          output fifo depth. \[4\]**  
  **\--syncSend                            send frame mode. \-1: block mode, \>=0：non-block, in ms.**  
  **\--syncGet                             get stream mode. \-1: block mode, \>=0：non-block, in ms.**

  **\--bLinkMode**  
  **\--strmBitDep                          encode stream bit depth. \[8\]**  
                                         **8 : encode 8bit**  
                                         **10: encode 10bit**

  **\--strmBufSize                         output stream buffer size. \[0\]**  
                                        **0: use default memory setting in sdk.**  
                                        **\>0：alloc some memory by user.**

  **\--virILen                             virtual I frame duration. should less than gop length.**

#### Example 1

Enable two channels to encode 1080p NV12 format (Channel 0: H.264, Channel 1: H.265)

**$ axcl\_sample\_venc \-w 1920 \-h 1080 \-i 1080p\_nv12.yuv \-N 2 \-l 3**

#### Example 2

Enable two channels to cyclically encode 3840x2160 NV21 format (Channel 0: H.264, Channel 1: H.265), encode 10 frames

**$ axcl\_sample\_venc \-w 3840 \-h 2160 \-i 3840x2160\_nv21.yuv \-N 2 \-l 4 \-n 10**

#### Example 3

Encode an MJPEG stream, resolution 1920x1080, YUV420P format, encode 5 frames

**$ axcl\_sample\_venc \-w 1920 \-h 1080 \-i 1920x1080\_yuv420p.yuv \-N 1 \--bChnCustom 1 \--codecType 2 \-l 1 \-n 5**

### axcl\_sample\_dmadim

DMA example, including:

Perform memory copy (memcpy) between two device memories via **AXCL\_DMA\_MemCopy**

Set device memory to 0xAB (memset) via **AXCL\_DMA\_MemCopy**

Calculate checksum via **AXCL\_DMA\_CheckSum**

Crop 1/4 of an image starting from (0, 0\) via **AXCL\_DMA\_MemCopyXD** (**AX\_DMADIM\_2D**)

#### Usage

**usage: ./axcl\_sample\_dmadim \--image=string \--width=unsigned int \--height=unsigned int \[options\] ...**  
**options:**  
  **\-d, \--device    device index from 0 to connected device num \- 1 (unsigned int \[=0\])**  
  **\-i, \--image     nv12 image file path (string)**  
  **\-w, \--width     width of nv12 image (unsigned int)**  
  **\-h, \--height    height of nv12 image (unsigned int)**  
      **\--json      axcl.json path (string \[=./axcl.json\])**  
  **\-?, \--help      print this message**

| Parameter | Default Value | Description |
| :---: | :---: | :---: |
| \-d, \--device | 0, range: \[0 \- connected device num \-1\] | Specify the device index |
| \--json | [axcl.json](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_samples#faq_axcl_json) | file path |
| \-i, \--image | NA | Input image file path |
| \-w, \--width | NA | Width of the input image |
| \-h, \--height | NA | Height of the input image |

#### Example

**$ axcl\_sample\_dmadim \-i 1920x1080.nv12.yuv \-w 1920 \-h 1080 \-d 0**  
**\[INFO \]\[                            main\]\[  30\]: \============== V3.5.0\_20250515190238 sample started May 15 2025 19:29:17 \==============**

**\[INFO \]\[                            main\]\[  46\]: json: ./axcl.json**  
**json file**  
**\[INFO \]\[                            main\]\[  66\]: device index: 0, bus number: 3**  
**\[INFO \]\[                        dma\_copy\]\[ 119\]: dma copy device memory succeed, from 0x14926f000 to 0x14966f000**  
**\[INFO \]\[                      dma\_memset\]\[ 139\]: dma memset device memory succeed, 0x14926f000 to 0xab**  
**\[INFO \]\[                    dma\_checksum\]\[ 166\]: dma checksum succeed, checksum \= 0xaaa00000**  
**\[INFO \]\[                      dma\_copy2d\]\[ 281\]: \[0\] dma memcpy 2D succeed**  
**\[INFO \]\[                      dma\_copy2d\]\[ 281\]: \[1\] dma memcpy 2D succeed**  
**\[INFO \]\[                      dma\_copy2d\]\[ 308\]: ./dma2d\_output\_image\_960x540.nv12 is saved**  
**\[INFO \]\[                      dma\_copy2d\]\[ 328\]: dma copy2d nv12 image pass**  
**\[INFO \]\[                            main\]\[  82\]: \============== V3.5.0\_20250515190238 sample exited May 15 2025 19:29:17 \==============**

### axcl\_sample\_ive

Example of Intelligent Video Engine (IVE).

**Note:**

* The sample code is for API demonstration purposes only, but in practice you need to use specific configuration parameters according to your application context.  
* For parameter limitations, please refer to the document titled **42 \- AX IVE API**.  
* The memory for filling input and output data must be allocated by the user.  
* The input and output image data must be specified by the user.  
* The number of input images (or data) from different CV modules may vary.  
* The data type of the 2D image must be explicitly defined, or use the default value.  
* These key parameters are formatted as a JSON string or JSON file. Please refer to the **.json** files and code in certain directories under **/opt/data/ive/**.

#### Usage

**m5stack@raspberrypi5:\~ $ axcl\_sample\_ive \--help**  
**Usage : axcl\_sample\_ive \-c case\_index \[options\]**  
        **\-d | \--device\_id: Device index from 0 to connected device num \- 1, optional**  
        **\-c | \--case\_index:Calc case index, default:0**  
                **0-DMA.**  
                **1-DualPicCalc.**  
                **2-HysEdge and CannyEdge.**  
                **3-CCL.**  
                **4-Erode and Dilate.**  
                **5-Filter.**  
                **6-Hist and EqualizeHist.**  
                **7-Integ.**  
                **8-MagAng.**  
                **9-Sobel.**  
                **10-GMM and GMM2.**  
                **11-Thresh.**  
                **12-16bit to 8bit.**  
                **13-Multi Calc.**  
                **14-Crop and Resize.**  
                **15-CSC.**  
                **16-CropResize2.**  
                **17-MatMul.**  
        **\-e | \--engine\_choice:Choose engine id, default:0**  
                **0-IVE; 1-TDP; 2-VGP; 3-VPP; 4-GDC; 5-DSP; 6-NPU; 7-CPU; 8-MAU.**  
                **For Crop and Resize case, cropimage support IVE/VGP/VPP engine, cropresize and cropresize\_split\_yuv support VGP/VPP engine.**  
                **For CSC case, support TDP/VGP/VPP engine.**  
                **For CropResize2 case, support VGP/VPP engine.**  
                **For MatMul case, support NPU/MAU engine.**  
        **\-m | \--mode\_choice:Choose test mode, default:0**  
                **For DualPicCalc case, indicate dual pictures calculation task:**  
                  **0-add; 1-sub; 2-and; 3-or; 4-xor; 5-mse.**  
                **For HysEdge and CannyEdge case, indicate hys edge or canny edge calculation task:**  
                  **0-hys edge; 1-canny edge.**  
                **For Erode and Dilate case, indicate erode or dilate calculation task:**  
                  **0-erode; 1-dilate.**  
                **For Hist and EqualizeHist case, indicate hist or equalize hist calculation task:**  
                  **0-hist; 1-equalize hist.**  
                **For GMM and GMM2 case, indicate gmm or gmm2 calculation task:**  
                  **0-gmm; 1-gmm2.**  
                **For Crop and Resize case, indicate cropimage, cropresize, cropresize\_split\_yuv calculation task:**  
                  **0-crop image; 1-crop\_resize; 2-cropresize\_split\_yuv.**  
                **For CropResize2 case, indicate crop\_resize2 or cropresize2\_split\_yuv calculation task:**  
                  **0-crop\_resize2; 1-cropresize2\_split\_yuv.**  
        **\-t | \--type\_image:Image type index refer to IVE\_IMAGE\_TYPE\_E(IVE engine) or AX\_IMG\_FORMAT\_E(other engine)**  
                **Note:**  
                  **1\. For all case, both input and output image types need to be specified in the same order as the specified input and output file order.**  
                  **2\. If no type is specified, i.e. a type value of \-1 is passed in, then a legal type is specified, as qualified by the API documentation.**  
                  **3\. Multiple input and output image types, separated by spaces.**  
                  **4\. For One-dimensional data (such as AX\_IVE\_MEM\_INFO\_T type data), do not require a type to be specified.**  
        **\-i | \--input\_files:Input image files, if there are multiple inputs, separated by spaces.**  
        **\-o | \--output\_files:Output image files or dir, if there are multiple outputs, separated by spaces**  
                **Note:for DMA, Crop Resize, blob of CCL case and CropResize2 case must be specified as directory.**  
        **\-w | \--width:Image width of inputs, default:1280.**  
        **\-h | \--height:Image height of inputs, default:720.**  
        **\-p | \--param\_list:Control parameters list or file(in json data format)**  
                **Note:**  
                  **1\. Please refer to the json file in the '/opt/data/ive/' corresponding directory of each test case.**  
                  **2\. For MagAng, Multi Calc and CSC case, no need control parameters.**  
        **\-a | \--align\_need:Does the width/height/stride need to be aligned automatically, default:0.**  
                  **0-no; 1-yes.**  
        **\-? | \--help:Show usage help.**

#### Example 1

DMA usage (Source resolution: 1280 x 720, Input / Output type: U8C1, Control parameters configured using JSON file)

**$ axcl\_sample\_ive \-c 0 \-w 1280 \-h 720 \-i /opt/data/ive/common/1280x720\_u8c1\_gray.yuv \-o /opt/data/ive/dma/ \-t 0 0 \-p /opt/data/ive/dma/dma.json**

#### Example 2

MagAndAng usage (Source resolution: 1280 x 720, Data type of input parameters (grad\_h, grad\_v): U16C1, Data type of output parameter (ang\_output): U8C1)

**$ axcl\_sample\_ive \-c 8 \-w 1280 \-h 720 \-i /opt/data/ive/common/1280x720\_u16c1\_gray.yuv /opt/data/ive/common/1280x720\_u16c1\_gray\_2.yuv \-o /opt/data/ive/common/mag\_output.bin /opt/data/ive/common/ang\_output.bin \-t 9 9 9 0**

#### json

1. **dma.json**  
   1. **mode**, **x0**, **y0**, **h\_seg**, **v\_seg**, **elem\_size** and **set\_val** are the value of respective member in structure **AX\_IVE\_DMA\_CTRL\_T** such as **enMode**, **u16CrpX0**, **u16CrpY0**, **u8HorSegSize**, **u8VerSegRows**, **u8ElemSize**, **u64Val**.  
   2. **w\_out** and **h\_out** is respectivly the width and height of output image, only for **AX\_IVE\_DMA\_MODE\_DIRECT\_COPY** mode in DMA.  
2. **dualpics.json**  
   1. **x** and **y** are the value of **u1q7X** and **u1q7Y** in structure **AX\_IVE\_ADD\_CTRL\_T** for ADD CV.  
   2. **mode** is the value of **enMode** in structure **AX\_IVE\_SUB\_CTRL\_T** for Sub CV.  
   3. **mse\_coef** is the value of **u1q15MseCoef** in structure **AX\_IVE\_MSE\_CTRL\_T** for MSE CV.  
3. **ccl.json**  
   1. **mode** is the value of **enMode** of structure **AX\_IVE\_CCL\_CTRL\_T** for CCL CV.  
4. **ed.json**  
   1. **mask** is all values of **au8Mask\[25\]** in structure **AX\_IVE\_ERODE\_CTRL\_T** for Erode CV or **AX\_IVE\_DILATE\_CTRL\_T** for Dilate CV.  
5. **filter.json**  
   1. **mask** is all values of **as6q10Mask\[25\]** in structure **AX\_IVE\_FILTER\_CTRL\_T** for Filter CV.  
6. **hist.json**  
   1. **histeq\_coef** is the value of **u0q20HistEqualCoef** in structure **AX\_IVE\_EQUALIZE\_HIST\_CTRL\_T** for EqualizeHist CV.  
7. **integ.json**  
   1. **out\_ctl** is the value of **enOutCtrl** in structure **AX\_IVE\_INTEG\_CTRL\_T** for Integ CV.  
8. **sobel.json**  
   1. **mask** is the value of **as6q10Mask\[25\]** in structure **AX\_IVE\_SOBEL\_CTRL\_T** for Sobel CV.  
9. **gmm.json**  
   1. **init\_var**, **min\_var**, **init\_w**, **lr**, **bg\_r**, **var\_thr** and **thr** are respectivly the value of **u14q4InitVar**, **u14q4MinVar**, **u1q10InitWeight**, **u1q7LearnRate**, **u1q7BgRatio**, **u4q4VarThr** and **u8Thr** in structure **AX\_IVE\_GMM\_CTRL\_T** for GMM CV.  
10. **gmm2.json:**  
    1. **init\_var**, **min\_var**, **max\_var**, **lr**, **bg\_r**, **var\_thr**, **var\_thr\_chk**, **ct** and **thr** are respectivly the value of **u14q4InitVar**, **u14q4MinVar**, **u14q4MaxVar**, **u1q7LearnRate**, **u1q7BgRatio**, **u4q4VarThr**, **u4q4VarThrCheck**, **s1q7CT** and **u8Thr** in structure **AX\_IVE\_GMM2\_CTRL\_T** for GMM2 CV.  
11. **thresh.json**  
    1. **mode**, **thr\_l**, **thr\_h**, **min\_val**, **mid\_val** and **max\_val** are repectivly the value of **enMode**, **u8LowThr**, **u8HighThr**, **u8MinVal**, **u8MidVal** and **u8MaxVal** in structure **AX\_IVE\_THRESH\_CTRL\_T** for Thresh CV.  
12. **16bit\_8bit.json**  
    1. **mode**, **gain** and **bias** are repectivly the value of **enMode**, **s1q14Gain** and **s16Bias** in structure **AX\_IVE\_16BIT\_TO\_8BIT\_CTRL\_T** for 16BitTo8Bit CV.  
13. **crop\_resize.json**  
    1. When CropImage is enabled, num is the value of **u16Num** in structure **AX\_IVE\_CROP\_IMAGE\_CTRL\_T** and boxs is the array type of crop image in which **x**,**y**,**w** and **h** are respecivly the value of **u16X**, **u16Y**, **u16Width** and **u16Height** in structure **AX\_IVE\_RECT\_U16\_T**.  
    2. When CropResize or CropResizeForSplitYUV mode is enabled, **num** is the value of **u16Num** in structure **AX\_IVE\_CROP\_RESIZE\_CTRL\_T** and **align0**, **align1**, **enAlign\[1\]**, **bcolor**, **w\_out** and **h\_out** are respectivly the value of **enAlign\[0\]**, **enAlign\[1\]**, **u32BorderColor**, **width** and **height** of output image.  
14. **crop\_resize2.json**  
    1. **num** is the value of **u16Num** in structure **AX\_IVE\_CROP\_IMAGE\_CTRL\_T**.  
    2. **res\_out** is the arrayes of width and height of output image.  
    3. **src\_boxs is the array of cropped range from source image, dst\_boxs is the array of range to resized image.**  
15. **matmul.json**  
    1. **mau\_i**, **ddr\_rdw**, **en\_mul\_res**, **en\_topn\_res**, **order** and **topn** are respectivly the value of **enMauId**, **s32DdrReadBandwidthLimit**, **bEnableMulRes**, **bEnableTopNRes**, **enOrder** and **s32TopN** in structure **AX\_IVE\_MAU\_MATMUL\_CTRL\_T**.  
    2. **type\_in** is the value of **stMatQ** and **stMatB** in structure **AX\_IVE\_MAU\_MATMUL\_INPUT\_T**.  
    3. **type\_mul\_res** and **type\_topn\_res** are the value of **stMulRes** and **sfTopNRes** in structure **AX\_IVE\_MAU\_MATMUL\_OUTPUT\_T**.  
    4. **q\_shape** and **b\_shape** are the value of **pShape** in **stMatQ** and **stMatB** of structure **AX\_IVE\_MAU\_MATMUL\_INPUT\_T**

### axcl\_sample\_ivps

Example of Image and Video Processing System (IVPS), providing functions such as cropping, scaling, rotation, streaming, CSC, OSD, mosaic, and quadrilateral operations.

#### Usage

**m5stack@raspberrypi5:\~ $ axcl\_sample\_ivps \-h**  
**AXCL IVPS Sample. Build at Jul 22 2025 02:31:34**  
**axcl\_sample\_ivps: option requires an argument \-- 'h'**  
**INFO   :\[IVPS\_ArgsParser:698\] pipeline\_ini: (null)**  
**INFO   :\[IVPS\_ArgsParser:699\] region\_ini: (null)**  
**Usage: /axcl\_sample\_ivps**  
        **\-d             (required) : device index from 0 to connected device num \- 1**  
        **\-v             (required) : video frame input**  
        **\-g             (optional) : overlay input**  
        **\-s             (optional) : sp alpha input**  
        **\-n             (optional) : repeat number**  
        **\-r             (optional) : region config and update**  
        **\-l             (optional) : 0: no link 1\. link ivps. 2: link venc. 3: link jenc**  
        **\--pipeline     (optional) : import ini file to config all the filters in one pipeline**  
        **\--pipeline\_ext (optional) : import ini file to config all the filters in another pipeline**  
        **\--change       (optional) : import ini file to change parameters for one filter dynamicly**  
        **\--region       (optional) : import ini file to config region parameters**  
        **\--dewarp       (optional) : import ini file to config dewarp parameters, including LDC, perspective, fisheye, etc.**  
        **\--cmmcopy      (optional) : cmm copy API test**  
        **\--csc          (optional) : color space covert API test**  
        **\--fliprotation (optional) : flip and rotation API test**  
        **\--alphablend   (optional) : alpha blending API test**  
        **\--cropresize   (optional) : crop resize API test**  
        **\--osd          (optional) : draw osd API test**  
        **\--cover        (optional) : draw line/polygon API test**  
        **\-a             (optional) : all the sync API test**

        **\--json         (optional) : axcl.json path**

            **\-v  \<PicPath\>@\<Format\>@\<Stride\>x\<Height\>@\<CropW\>x\<CropH\>\[+\<CropX0\>+\<CropY0\>\]\>**  
           **e.g: \-v /opt/bin/data/ivps/800x480car.nv12@3@800x480@600x400+100+50**

           **\[-g\] \<PicPath\>@\<Format\>@\<Stride\>x\<Height\>\[+\<DstX0\>+\<DstY0\>\*\<Alpha\>\]\>**  
           **e.g: \-g /opt/bin/data/ivps/rgb400x240.rgb24@161@400x240+100+50\*150**

           **\[-n\] \<repeat num\>\]**  
           **\[-r\] \<region num\>\]**

        **\<PicPath\>                     : source picture path**  
        **\<Format\>                      : picture color format**  
                   **3: NV12     YYYY... UVUVUV...**  
                   **4: NV21     YYYY... VUVUVU...**  
                  **10: NV16     YYYY... UVUVUV...**  
                  **11: NV61     YYYY... VUVUVU...**  
                 **161: RGB888   24bpp**  
                 **165: BGR888   24bpp**  
                 **160: RGB565   16bpp**  
                 **197: ARGB4444 16bpp**  
                 **203: RGBA4444 16bpp**  
                 **199: ARGB8888 32bpp**  
                 **201: RGBA8888 32bpp**  
                 **198: ARGB1555 16bpp**  
                 **202: RGBA5551 16bpp**  
                 **200: ARGB8565 24bpp**  
                 **204: RGBA5658 24bpp**  
                 **205: ABGR4444 16bpp**  
                 **211: BGRA4444 16bpp**  
                 **207: ABGR8888 32bpp**  
                 **209: BGRA8888 32bpp**  
                 **206: ABGR1555 16bpp**  
                 **210: BGRA5551 16bpp**  
                 **208: ABGR8565 24bpp**  
                 **212: BGRA5658 24bpp**  
                 **224: BITMAP    1bpp**  
        **\<Stride\>           (required) : picture stride (16 bytes aligned)**  
        **\<Stride\>x\<Height\>  (required) : input frame stride and height (2 aligned)**  
        **\<CropW\>x\<CropH\>    (required) : crop rect width & height (2 aligned)**  
        **\+\<CropX0\>+\<CropY0\> (optional) : crop rect coordinates**  
        **\+\<DstX0\>+\<DstY0\>   (optional) : output position coordinates**  
        **\<Alpha\>            (optional) : ( (0, 255\], 0: transparent; 255: opaque)**

**Example1:**  
        **/axcl\_sample\_ivps \-d 0 \-v /opt/data/ivps/1920x1088.nv12@3@1920x1088@1920x1088  \-n 1**  
**Note:**

* **\-v** is a required option with the input source image path and frame information.  
  The cropping window should be within the height range of the source image, i.e., CropX0 \+ CropW \<= Stride, CropY0 \+ CropH \<= Height.  
  If no cropping is performed, then CropW \= Width, CropH \= Height, CropX0 \= 0, and CropY0 \= 0\.  
* **\-n** specifies the number of times to process the source image. If the parameter is \-1, it will loop indefinitely.  
  To view the proc information of IVPS, set the processing count to a large value or keep it looping.  
* The input parameter after **\-r** is the number of overlaid REGIONs, with the current maximum being 4\.  
  Overlaying REGION on the IVPS PIPELINE is an asynchronous operation, so it takes several frames to actually overlay onto the input source image.  
  Therefore, to verify the REGION function, set the parameter after \-n to be larger than 3\. The value should be greater than 3.2.

#### Example 1

Process a source image (3840x2160 NV12 format) once

**$ axcl\_sample\_ivps \-v /opt/data/ivps/3840x2160.nv12@3@3840x2160@0x0+0+0 \-d 0 \-n 1**

#### Example 2

Process a source image (800x480 RGB 888 format) with cropping (X0=128 Y0=50 W=400 H=200), process three times

**$ axcl\_sample\_ivps \-v /opt/data/ivps/800x480logo.rgb24@161@800x480@400x200+128+50 \-d 0 \-n 3**

#### Example 3

Process a source image (3840x2160 NV12 format) five times and overlay three REGIONs

**$ axcl\_sample\_ivps \-v /opt/data/ivps/3840x2160.nv12@3@3840x2160@0x0+0+0 \-d 0 \-n 5 \-r 3**

### axcl\_sample\_transcode

Example of transcoding. The pipeline (PPL) is as follows:

1. Load .mp4 file or .h264/.h265 raw bitstream file.  
2. Demux nalu via ffmpeg  
3. Send nalu frames to VDEC  
4. VDEC sends the decoded nv12 to IVPS (if resizing)  
5. IVPS sends the nv12 to VENC  
6. Send the encoded nalu frames to the host via VENC.

#### deployment

**| \----------------------------- |**  
**| sample                        |**  
**| \----------------------------- |**  
**| libaxcl\_ppl.so                |**  
**| \----------------------------- |**  
**| libaxcl\_lite.so               |**  
**| \----------------------------- |**  
**| AXCL SDK                      |**  
**| \----------------------------- |**

#### attributes

       **attribute name                       R/W    attribute value type**  
 **\*  axcl.ppl.transcode.vdec.grp             \[R  \]       int32\_t                            allocated by ax\_vdec.ko**  
 **\*  axcl.ppl.transcode.ivps.grp             \[R  \]       int32\_t                            allocated by ax\_ivps.ko**  
 **\*  axcl.ppl.transcode.venc.chn             \[R  \]       int32\_t                            allocated by ax\_venc.ko**  
 **\***  
 **\*  the following attributes take effect BEFORE the axcl\_ppl\_create function is called:**  
 **\*  axcl.ppl.transcode.vdec.blk.cnt         \[R/W\]       uint32\_t          8                depend on stream DPB size and decode mode**  
 **\*  axcl.ppl.transcode.vdec.out.depth       \[R/W\]       uint32\_t          4                out fifo depth**  
 **\*  axcl.ppl.transcode.ivps.in.depth        \[R/W\]       uint32\_t          4                in fifo depth**  
 **\*  axcl.ppl.transcode.ivps.out.depth       \[R  \]       uint32\_t          0                out fifo depth**  
 **\*  axcl.ppl.transcode.ivps.blk.cnt         \[R/W\]       uint32\_t          4**  
 **\*  axcl.ppl.transcode.ivps.engine          \[R/W\]       uint32\_t   AX\_IVPS\_ENGINE\_VPP      AX\_IVPS\_ENGINE\_VPP|AX\_IVPS\_ENGINE\_VGP|AX\_IVPS\_ENGINE\_TDP**  
 **\*  axcl.ppl.transcode.venc.in.depth        \[R/W\]       uint32\_t          4                in fifo depth**  
 **\*  axcl.ppl.transcode.venc.out.depth       \[R/W\]       uint32\_t          4                out fifo depth**

**NOTE:**  
 **The value of "axcl.ppl.transcode.vdec.blk.cnt" depends on input stream.**  
 **Usually set to dpb \+ 1**

#### Usage

**$ axcl\_sample\_transcode \--help**  
**usage: axcl\_sample\_transcode \--url=string \[options\] ...**  
**options:**  
  **\-i, \--url       mp4|.264|.265 file path (string)**  
  **\-d, \--device    device index from 0 to connected device num \- 1 (unsigned int \[=0\])**  
  **\-w, \--width     output width, 0 means same as input (unsigned int \[=0\])**  
  **\-h, \--height    output height, 0 means same as input (unsigned int \[=0\])**  
      **\--codec     encoded codec: \[h264 | h265\] (default: h265) (string \[=h265\])**  
      **\--json      axcl.json path (string \[=./axcl.json\])**  
      **\--loop      1: loop demux for local file  0: no loop(default) (int \[=0\])**  
      **\--dump      dump file path (string \[=\])**  
      **\--hwclk     decoder hw clk, 0: 624M, 1: 500M, 2: 400M(default) (unsigned int \[=2\])**  
      **\--ut        unittest**  
  **\-?, \--help      print this message**

| Parameter | Default Value | Description |
| :---: | :---: | :---: |
| \-d, \--device | 0, range: \[0 \- connected device num \-1\] | Specify the device index. |
| \--json | [axcl.json](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_samples#faq_axcl_json) | file path |
| \-i, \--url | NA | Specify the path of the stream file. |
| \-w, \--width | 1920 | Specify the width of the decoded YUV image. |
| \-h, \--height | 1080 | Specify the height of the decoded YUV image. |
| \--codec | h265 | Specify the payload type. |
| \--loop | 0 | 1: Loop transcode until CTRL+C, 0: Do not loop. |
| \--dump |  | Specify the path to dump the file. |
| \--hwclk | 2 (400M) | Set the clock of the VDEC in MHz. |
| \--ut |  | Internal use |

If you encounter the following error:

**m5stack@raspberrypi5:\~ $ axcl\_sample\_transcode \--help**  
**axcl\_sample\_transcode: error while loading shared libraries: libavcodec.so.61: cannot open shared object file: No such file or directory**

**m5stack@raspberrypi5:\~ $ export LD\_LIBRARY\_PATH=/usr/lib/axcl/ffmpeg:$LD\_LIBRARY\_PATH**  
Please first set the environment variable via  
**export LD\_LIBRARY\_PATH=/usr/lib/axcl/ffmpeg:$LD\_LIBRARY\_PATH**

#### Example

Transcode the input 1080P@30fps 264 to 1080P@30fps 265 and save it to the **/tmp/axcl/transcode.dump.pidxxx** file.

**$ axcl\_sample\_transcode \-i bangkok\_30952\_1920x1080\_30fps\_gop60\_4Mbps.mp4 \-d 0 \--dump /tmp/axcl/transcode.265**  
**\[INFO \]\[                            main\]\[  67\]: \============== V3.5.0\_20250515190238 sample started May 15 2025 19:29:29 pid 91189 \==============**

**\[WARN \]\[                            main\]\[  92\]: if enable dump, disable loop automatically**  
**json file**  
**\[INFO \]\[                            main\]\[ 131\]: pid: 91189, device index: 0, bus number: 3**  
**\[INFO \]\[             ffmpeg\_init\_demuxer\]\[ 439\]: \[91189\] url: bangkok\_30952\_1920x1080\_30fps\_gop60\_4Mbps.mp4**  
**\[INFO \]\[             ffmpeg\_init\_demuxer\]\[ 502\]: \[91189\] url bangkok\_30952\_1920x1080\_30fps\_gop60\_4Mbps.mp4: codec 96, 1920x1080, fps 30**  
**\[INFO \]\[         ffmpeg\_set\_demuxer\_attr\]\[ 571\]: \[91189\] set ffmpeg.demux.file.frc to 1**  
**\[INFO \]\[         ffmpeg\_set\_demuxer\_attr\]\[ 574\]: \[91189\] set ffmpeg.demux.file.loop to 0**  
**\[INFO \]\[                            main\]\[ 195\]: pid 91189: \[vdec 00\] \- \[ivps \-1\] \- \[venc 00\]**  
**\[INFO \]\[                            main\]\[ 213\]: pid 91189: VDEC attr \==\> blk cnt: 8, fifo depth: out 4**  
**\[INFO \]\[                            main\]\[ 214\]: pid 91189: IVPS attr \==\> blk cnt: 5, fifo depth: in 4, out 0, engine 1**  
**\[INFO \]\[                            main\]\[ 216\]: pid 91189: VENC attr \==\> fifo depth: in 4, out 4**  
**\[INFO \]\[          ffmpeg\_dispatch\_thread\]\[ 189\]: \[91189\] \+++**  
**\[INFO \]\[             ffmpeg\_demux\_thread\]\[ 295\]: \[91189\] \+++**  
**\[INFO \]\[             ffmpeg\_demux\_thread\]\[ 328\]: \[91189\] reach eof**  
**\[INFO \]\[             ffmpeg\_demux\_thread\]\[ 435\]: \[91189\] demuxed    total 470 frames \---**  
**\[INFO \]\[          ffmpeg\_dispatch\_thread\]\[ 272\]: \[91189\] dispatched total 470 frames \---**  
**\[INFO \]\[                            main\]\[ 247\]: ffmpeg (pid 91189\) demux eof**  
**\[2025-05-20 22:49:08.834\]\[91195\]\[W\]\[axclite-venc-dispatch\]\[dispatch\_thread\]\[44\]: no stream in veChn 0 fifo**  
**\[INFO \]\[                            main\]\[ 283\]: total transcoded frames: 470**  
**\[INFO \]\[                            main\]\[ 284\]: \============== V3.5.0\_20250515190238 sample exited May 15 2025 19:29:29 pid 91189 \==============**  
**launch\_transcode.sh** supports starting multiple (up to 16\) **axcl\_sample\_transcode** processes and automatically configuring **LD\_LIBRARY\_PATH**.

**$ ./launch\_transcode.sh 16 \-i bangkok\_30952\_1920x1080\_30fps\_gop60\_4Mbps.mp4  \-d 3 \--dump /tmp/axcl/transcode.265**  
The first parameter must be the number of **axcl\_sample\_transcode** processes. Range: \[1, 16\]

# **SDK API**

## Overview

**AXCL API** is divided into two parts: the **Runtime API** and the **Native API**. The **Runtime API** is an independent set of **APIs**, currently only including **Memory** for memory management and **Engine API** for driving the **Axera(TM)** **NPU** to work. When the **AXCL API** is used in the form of a compute card without using codec functions, all computation tasks can be completed using only the **Runtime API**. When codec functions are required, you need to understand the **Native API** and the related contents of the **FFMPEG** module.

## runtime

Using the **Runtime API** allows the **NPU** to be called on the host system to perform computing functions. The **Memory API** can allocate and free memory space on both the host and the compute card, while the **Engine API** can complete all **NPU** functionalities from model initialization and **IO** settings to inference.

### runtime

#### axclInit

**axclError axclInit(const char \*config);**  
**Description**:

System initialization, synchronous interface.

**Parameters**:

* **config \[IN\]**: Specifies the path to the JSON configuration file.  
  * Users can configure system parameters through the JSON configuration file. Currently, log level settings are supported. Format [refer to FAQ](https://github.com/AXERA-TECH/axcl-docs/wiki/0.FAQ#how-to-configure-runtime-log--level).  
  * NULL or a non-existent JSON file can be passed, in which case the system uses the default configuration.

**Limitations**:

* Must be paired with [**axclFinalize**](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_axcl_api#axclfinalize) for system cleanup.  
* This interface must be called before invoking any AXCL interface-based application.  
* Can be called only once within a single process.

---

#### axclFinailze

**axclError axclFinalize();**  
**Description**:

System de-initialization, releasing AXCL resources within the process, synchronous interface.

**Limitations**:

* Must be paired with [**axclInit**](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_axcl_api#axclinit).  
* Before the application process exits, this interface should be explicitly called for de-initialization.  
* For C++ applications, it is not recommended to call this in the destructor. Otherwise, the process may exit abnormally upon termination due to an uncertain destruction order of singletons.

---

#### axclrtGetVersion

**axclError axclrtGetVersion(int32\_t \*major, int32\_t \*minor, int32\_t \*patch);**  
**Description**:

Query the system version number, synchronous interface.

**Parameters**:

* **major \[OUT\]**: Major version number.  
* **minor \[OUT\]**: Minor version number.  
* **patch \[OUT\]**: Patch version number.

**Limitations**:

No special restrictions.

---

#### axclrtGetSocName

**const char \*axclrtGetSocName();**  
**Description**:

Query the current chip SOC name string, synchronous interface.

**Limitations**:

No special restrictions.

---

#### axclrtSetDevice

**axclError axclrtSetDevice(int32\_t deviceId);**  
**Description**:

Specify the device in the current process or thread, while implicitly creating a default Context, synchronous interface.

**Parameters**:

* **deviceId \[IN\]**: Device ID.

**Limitations**:

* This interface implicitly creates a default Context internally, which is automatically released by the system in [**axclrtResetDevice**](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_axcl_api#axclrtresetdevice) and must not be explicitly destroyed using [**axclrtDestroyContext**](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_axcl_api#axclrtdestroycontext).  
* In multiple threads within the same process, if the **deviceId** specified in this interface is the same, the implicitly created Context will also be the same.  
* Must be paired with [**axclrtResetDevice**](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_axcl_api#axclrtresetdevice) to release the device resources used by this process; internally uses reference counting to allow multiple calls, and only releases resources when the reference count reaches 0\.  
* In a multi-device scenario, you can switch devices within the process using this interface or [**axclrtSetCurrentContext**](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_axcl_api#axclrtsetcurrentcontext).

---

#### axclrtResetDevice

**axclError axclrtResetDevice(int32\_t deviceId);**  
**Description**:

Reset the device and release resources on the device, including both implicitly and explicitly created Contexts, synchronous interface.

**Parameters**:

* **deviceId \[IN\]**: Device ID.

**Limitations**:

* For Contexts explicitly created using [**axclrtCreateContext**](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_axcl_api#axclrtcreatecontext), it is recommended to explicitly destroy them using [**axclrtDestroyContext**](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_axcl_api#axclrtdestroycontext) before calling this interface to release device resources.  
* Must be paired with [**axclrtSetDevice**](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_axcl_api#axclrtsetdevice); the system will automatically reclaim default Context resources.  
* Internally uses reference counting to allow multiple calls, and only releases resources when the reference count reaches 0\.  
* **When the application process exits, make sure axclrtResetDevice is called, especially after handling exception signals; otherwise, this may cause a C++ terminated abort exception.**

---

#### axclrtGetDevice

**axclError axclrtGetDevice(int32\_t \*deviceId);**  
**Description**:

Get the current device ID in use, synchronous interface.

**Parameters**:

* **deviceId \[OUT\]**: Device ID.

**Limitations**:

* If neither [**axclrtSetDevice**](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_axcl_api#axclrtsetdevice) nor [**axclrtCreateContext**](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_axcl_api#axclrtcreatecontext) has been called to specify a device, this interface will return an error.

---

#### axclrtGetDeviceCount

**axclError axclrtGetDeviceCount(uint32\_t \*count);**  
**Description**:

Get the total number of connected devices, synchronous interface.

**Parameters**:

* **count \[OUT\]**: Number of devices.

**Limitations**:

No special restrictions.

---

#### axclrtGetDeviceList

**axclError axclrtGetDeviceList(axclrtDeviceList \*deviceList);**  
**Description**:

Get the IDs of all connected devices, synchronous interface.

**Parameters**:

* **deviceList \[OUT\]**: Information of all connected device IDs.

**Limitations**:

No special restrictions.

---

#### axclrtSynchronizeDevice

**axclError axclrtSynchronizeDevice();**  
**Description**:

Synchronously execute all tasks on the current device, synchronous interface.

**Limitations**:

At least one device must be active.

---

#### axclrtGetDeviceProperties

**axclError axclrtGetDeviceProperties(int32\_t deviceId, axclrtDeviceProperties \*properties);**  
**Description**:

Retrieve information such as device UID, CPU usage, NPU usage, and memory, synchronous interface.

**Limitations**:

No special restrictions.

---

#### axclrtCreateContext

**axclError axclrtCreateContext(axclrtContext \*context, int32\_t deviceId);**  
**Description**:

Explicitly create a Context in the current thread, synchronous interface.

**Parameters**:

* **context \[OUT\]**: Handle for the created Context.  
* **deviceId \[IN\]**: Device ID.

**Limitations**:

* If a user-created sub-thread needs to call the AXCL API, it must explicitly create a Context using this interface or bind one using [**axclrtSetCurrentContext**](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_axcl_api#axclrtsetcurrentcontext).  
* If the specified device has not been activated, this interface will activate it first internally.  
* Call [**axclrtDestroyContext**](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_axcl_api#axclrtdestroycontext) to explicitly release Context resources.  
* Multiple threads can share the same Context (bound by [**axclrtSetCurrentContext**](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_axcl_api#axclrtsetcurrentcontext)), but task execution depends on the system’s thread scheduling order. Users must manage and maintain execution synchronization order between threads themselves. For multi-threading, it is recommended to create a dedicated Context for each thread to improve maintainability.

---

#### axclrtDestroyContext

**axclError axclrtDestroyContext(axclrtContext context);**  
**Description**:

Explicitly destroy a Context, synchronous interface.

**Parameters**:

* **context \[IN\]**: Handle for the created Context.

**Limitations**:

* Only Context resources created using [**axclrtCreateContext**](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_axcl_api#axclrtcreatecontext) can be destroyed.

---

#### axclrtSetCurrentContext

**axclError axclrtSetCurrentContext(axclrtContext context);**  
**Description**:

Bind the Context for a thread to run with, synchronous interface.

**Parameters**:

* **context \[IN\]**: Context handle.

**Limitations**:

* If this interface is called multiple times to bind a Context to a thread, the last binding takes precedence.  
* If the device corresponding to the bound Context has been reset using [**axclrtResetDevice**](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_axcl_api#axclrtresetdevice), the Context cannot be set for the thread, otherwise exceptions will occur.  
* It is recommended to use the Context in the same thread where it was created. If **axclrtCreateContext** is called in Thread A and the Context is used in Thread B, the user must ensure the task execution order under the same Context is maintained between the two threads.

---

#### axclrtGetCurrentContext

**axclError axclrtGetCurrentContext(axclrtContext \*context);**  
**Description**:

Get the Context handle bound to the thread, synchronous interface.

**Parameters**:

* **context \[OUT\]**: The current Context handle.

**Limitations**:

* The calling thread must have previously bound a Context using [**axclrtSetCurrentContext**](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_axcl_api#axclrtsetcurrentcontext) or created one using [**axclrtCreateContext**](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_axcl_api#axclrtcreatecontext) before it can be retrieved.  
* If [**axclrtSetCurrentContext**](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_axcl_api#axclrtsetcurrentcontext) has been called multiple times, the Context retrieved will be the one set most recently.

---

### memory

#### axclrtMalloc

**axclError axclrtMalloc(void \*\*devPtr, size\_t size, axclrtMemMallocPolicy policy);**  
**Description**:

Allocate non-CACHED physical memory on the device side. The allocated memory pointer is returned via **devPtr**, synchronous interface.

**Parameters**:

* **devPtr \[OUT\]**: Pointer to the allocated device-side physical memory.  
* **size \[IN\]**: Size of the allocated memory in bytes.  
* **policy \[IN\]**: Memory allocation policy, currently unused.

**Limitations**:

* Allocates continuous physical memory from the device-side CMM memory pool.  
* Allocates non-CACHED memory, no consistency handling is required.  
* Use [**axclrtFree**](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_axcl_api#axclrtfree) to release memory.  
* Frequent allocation and release will impact performance; it is recommended to use pre-allocation or secondary memory management to avoid frequent operations.

---

#### axclrtMallocCached

**axclError axclrtMallocCached(void \*\*devPtr, size\_t size, axclrtMemMallocPolicy policy);**  
**Description**:

Allocate CACHED physical memory on the device side. The allocated memory pointer is returned via **devPtr**, synchronous interface.

**Parameters**:

* **devPtr \[OUT\]**: Pointer to the allocated device-side physical memory.  
* **size \[IN\]**: Size of the allocated memory in bytes.  
* **policy \[IN\]**: Memory allocation policy, currently unused.

**Limitations**:

* Allocates continuous physical memory from the device-side CMM memory pool.  
* Allocates CACHED memory, and the user must handle data consistency.  
* Use [**axclrtFree**](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_axcl_api#axclrtfree) to release memory.  
* Frequent allocation and release will impact performance; it is recommended to use pre-allocation or secondary memory management to avoid frequent operations.

---

#### axclrtFree

**axclError axclrtFree(void \*devPtr);**  
**Description**:

Release memory allocated on the device side, synchronous interface.

**Parameters**:

* **devPtr \[IN\]**: Device memory to be released.

**Limitations**:

* Can only release memory allocated using [**axclrtMalloc**](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_axcl_api#axclrtmalloc) or [**axclrtMallocCached**](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_axcl_api#axclrtmalloccached).

---

#### axclrtMemFlush

**axclError axclrtMemFlush(void \*devPtr, size\_t size);**  
**Description**:

Flush the data in the cache to DDR and invalidate the contents in the cache, synchronous interface.

**Parameters**:

* **devPtr \[IN\]**: Starting address pointer of the DDR memory to be flushed.  
* **size \[IN\]**: Size of the DDR memory to be flushed, in bytes.

**Limitations**:

No special restrictions.

---

#### axclrtMemInvalidate

**axclError axclrtMemInvalidate(void \*devPtr, size\_t size);**  
**Description**:

Invalidate the data in the cache, synchronous interface.

**Parameters**:

* **devPtr \[IN\]**: Starting address pointer of the DDR memory whose cache data will be invalidated.  
* **size \[IN\]**: Size of the DDR memory, in bytes.

**Limitations**:

* No special restrictions.

---

#### axclrtMallocHost

**axclError axclrtMallocHost(void \*\*hostPtr, size\_t size);**  
**Description**:

Allocate virtual memory on the HOST, synchronous interface.

**Parameters**:

* **hostPtr \[OUT\]**: Start address of the allocated memory.  
* **size \[IN\]**: Size of the allocated memory, in bytes.

**Limitations**:

* Memory allocated with [**axclrtMallocHost**](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_axcl_api#axclrtmallochost) must be released with [**axclrtFreeHost**](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_axcl_api#axclrtfreehost).  
* Frequent memory allocations and releases can impact performance; it is recommended to use pre-allocation or secondary memory management to avoid frequent operations.  
* Memory can also be allocated on the HOST using the standard **malloc** interface, but [**axclrtMallocHost**](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_axcl_api#axclrtmallochost) is recommended.

---

#### axclrtFreeHost

**axclError axclrtFreeHost(void \*hostPtr);**  
**Description**:

Release memory allocated by [**axclrtMallocHost**](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_axcl_api#axclrtmallochost), synchronous interface.

**Parameters**:

* **hostPtr \[IN\]**: Start address of the memory to be released.

**Limitations**:

* Can only release HOST memory allocated by [**axclrtMallocHost**](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_axcl_api#axclrtmallochost).

---

#### axclrtMemset

**axclError axclrtMemset(void \*devPtr, uint8\_t value, size\_t count);**  
**Description**:

Only used to initialize device-side memory allocated by [**axclrtMalloc**](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_axcl_api#axclrtmalloc) or [**axclrtMallocCached**](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_axcl_api#axclrtmalloccached), synchronous interface.

**Parameters**:

* **devPtr \[IN\]**: Start address of the device-side memory to initialize.  
* **value \[IN\]**: Value to set.  
* **count \[IN\]**: Length of the memory to initialize, in bytes.

**Limitations**:

* Only memory allocated by [**axclrtMalloc**](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_axcl_api#axclrtmalloc) or [**axclrtMallocCached**](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_axcl_api#axclrtmalloccached) can be initialized.  
* Device-side memory allocated by [**axclrtMallocCached**](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_axcl_api#axclrtmalloccached) requires a call to [**axclrtMemInvalidate**](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_axcl_api#axclrtmeminvalidate) after initialization to maintain consistency.  
* For HOST memory allocated by [**axclrtMallocHost**](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_axcl_api#axclrtmallochost), please use the standard **memset** function for initialization.

---

#### axclrtMemcpy

**axclError axclrtMemcpy(void \*dstPtr, const void \*srcPtr, size\_t count, axclrtMemcpyKind kind);**  
**Description**:

Performs synchronous memory copy operations between HOST memory, between HOST and DEVICE memory, and within DEVICE memory.

**Parameters**:

* **devPtr \[IN\]**: Destination memory address pointer.  
* **srcPtr \[IN\]**: Source memory address pointer.  
* **count \[IN\]**: Length of memory to be copied, in bytes.  
* **kind \[IN\]**: Type of memory copy.  
  * \[**AXCL\_MEMCPY\_HOST\_TO\_HOST**\]: Memory copy within HOST memory.  
  * \[**AXCL\_MEMCPY\_HOST\_TO\_DEVICE**\]: Copy from HOST virtual memory to DEVICE memory.  
  * \[**AXCL\_MEMCPY\_DEVICE\_TO\_HOST**\]: Copy from DEVICE memory to HOST virtual memory.  
  * \[**AXCL\_MEMCPY\_DEVICE\_TO\_DEVICE**\]: Memory copy within DEVICE.  
  * \[**AXCL\_MEMCPY\_HOST\_PHY\_TO\_DEVICE**\]: Copy from HOST continuous physical memory to DEVICE.  
  * \[**AXCL\_MEMCPY\_DEVICE\_TO\_HOST\_PHY**\]: Copy from DEVICE to HOST continuous physical memory.

**Limitations**:

* The source and destination memory must comply with the requirements of **kind**.

---

#### axclrtMemcmp

**axclError axclrtMemcmp(const void \*devPtr1, const void \*devPtr2, size\_t count);**  
**Description**:

Performs memory comparison within the DEVICE, synchronous interface.

**Parameters**:

* **devPtr1 \[IN\]**: Pointer to device memory address \#1.  
* **devPtr2 \[IN\]**: Pointer to device memory address \#2.  
* **count \[IN\]**: Length to compare, in bytes.

**Limitations**:

* Only supports comparison of device memory; returns **AXCL\_SUCC(0)** only if the memory contents are the same.

---

### engine

#### axclrtEngineInit

**axclError axclrtEngineInit(axclrtEngineVNpuKind npuKind);**  
**Description**:

Initializes the **Runtime Engine**. Must be called before using the **Runtime Engine**.

**Parameters**:

* **npuKind \[IN\]**: Specifies the type of **VNPU** to initialize.

**Limitations**:

After using the **Runtime Engine**, the user must call [**axclrtEngineFinalize**](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_axcl_api#axclrtenginefinalize) to clean up the **Runtime Engine**.

---

#### axclrtEngineGetVNpuKind

**axclError axclrtEngineGetVNpuKind(axclrtEngineVNpuKind \*npuKind);**  
**Description**:

Retrieves the initialized **VNPU** type of the **Runtime Engine**.

**Parameters**:

* **npuKind \[OUT\]**: Returns the **VNPU** type.

**Limitations**:

The user must call [**axclrtEngineInit**](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_axcl_api#axclrtengineinit) to initialize the **Runtime Engine** before calling this function.

---

#### axclrtEngineFinalize

**axclError axclrtEngineFinalize();**  
**Description**:

Cleans up the **Runtime Engine**. Must be called after completing all operations.

**Limitations**:

The user must call [**axclrtEngineInit**](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_axcl_api#axclrtengineinit) before calling this function.

---

#### axclrtEngineLoadFromFile

**axclError axclrtEngineLoadFromFile(const char \*modelPath, uint64\_t \*modelId);**  
**Description**:

Loads model data from a file and creates a model **ID**.

**Parameters**:

* **modelPath \[IN\]**: Path to the offline model file.  
* **modelId \[OUT\]**: The model **ID** generated after loading, used as an identifier for subsequent operations.

**Limitations**:

The user must call [**axclrtEngineInit**](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/m5_llm_8850_axcl_api#axclrtengineinit) to initialize the **Runtime Engine** before calling this function.

---

#### axclrtEngineLoadFromMem

**axclError axclrtEngineLoadFromMem(const void \*model, uint64\_t modelSize, uint64\_t \*modelId);**  
**Description**:

Loads offline model data from memory, with memory for model execution managed internally by the system.

**Parameters**:

* **model \[IN\]**: Model data stored in memory.  
* **modelSize \[IN\]**: Size of the model data.  
* **modelId \[OUT\]**: The model **ID** generated after loading, used as an identifier for subsequent operations.

**Limitations**:

* The model memory must be device memory, which the user must manage and release.

---

#### axclrtEngineUnload

**axclError axclrtEngineUnload(uint64\_t modelId);**  
**Description**:

This function is used to unload a model with the specified model **ID**.

**Parameters**:

* **modelId \[IN\]**: The model **ID** to unload.

**Limitations**:

No special restrictions.

---

#### axclrtEngineGetModelCompilerVersion

**const char\* axclrtEngineGetModelCompilerVersion(uint64\_t modelId);**  
**Description**:

This function retrieves the version of the toolchain used to build the model.

**Parameters**:

* **modelId \[IN\]**: Model **ID**.

**Limitations**:

No special restrictions.

---

#### axclrtEngineSetAffinity

**axclError axclrtEngineSetAffinity(uint64\_t modelId, axclrtEngineSet set);**  
**Description**:

This function is used to set the model’s NPU affinity.

**Parameters**:

* **modelId \[IN\]**: Model **ID**.  
* **set \[OUT\]**: Affinity set to apply.

**Limitations**:

Cannot be zero, and the mask bits set must not exceed the affinity range.

---

#### axclrtEngineGetAffinity

**axclError axclrtEngineGetAffinity(uint64\_t modelId, axclrtEngineSet \*set);**  
**Description**:

This function retrieves the model’s NPU affinity.

**Parameters**:

* **modelId \[IN\]**: Model **ID**.  
* **set \[OUT\]**: Returned affinity set.

**Limitations**:

No special restrictions.

---

#### axclrtEngineGetUsage

**axclError axclrtEngineGetUsage(const char \*modelPath, int64\_t \*sysSize, int64\_t \*cmmSize);**  
**Description**:

This function retrieves the required system memory size and CMM memory size for executing a model based on its file.

**Parameters**:

* **modelPath \[IN\]**: Model path used to obtain memory information.  
* **sysSize \[OUT\]**: Working system memory size required to run the model.  
* **cmmSize \[OUT\]**: CMM memory size required to run the model.

**Limitations**:

No special restrictions.

---

#### axclrtEngineGetUsageFromMem

**axclError axclrtEngineGetUsageFromMem(const void \*model, uint64\_t modelSize, int64\_t \*sysSize, int64\_t \*cmmSize);**  
**Description**:

This function retrieves the required system memory size and CMM memory size for executing a model based on its data in memory.

**Parameters**:

* **model \[IN\]**: User-managed model memory.  
* **modelSize \[IN\]**: Size of the model data.  
* **sysSize \[OUT\]**: Working system memory size required to run the model.  
* **cmmSize \[OUT\]**: CMM memory size required to run the model.

**Limitations**:

Model memory must reside in device memory, which the user must manage and release.

---

#### axclrtEngineGetUsageFromModelId

**axclError axclrtEngineGetUsageFromModelId(uint64\_t modelId, int64\_t \*sysSize, int64\_t \*cmmSize);**  
**Description**:

This function retrieves the required system memory size and CMM memory size for executing a model based on its **ID**.

**Parameters**:

* **modelId \[IN\]**: Model **ID**.  
* **sysSize \[OUT\]**: Working system memory size required to run the model.  
* **cmmSize \[OUT\]**: CMM memory size required to run the model.

**Limitations**:

No special restrictions.

---

#### axclrtEngineGetModelType

**axclError axclrtEngineGetModelType(const char \*modelPath, axclrtEngineModelKind \*modelType);**  
**Description**:

This function retrieves the model type based on its file.

**Parameters**:

* **modelPath \[IN\]**: Model path used to retrieve model type.  
* **modelType \[OUT\]**: Returned model type.

**Limitations**:

No special restrictions.

---

#### axclrtEngineGetModelTypeFromMem

**axclError axclrtEngineGetModelTypeFromMem(const void \*model, uint64\_t modelSize, axclrtEngineModelKind \*modelType);**  
**Description**:

This function retrieves the model type based on model data in memory.

**Parameters**:

* **model \[IN\]**: User-managed model memory.  
* **modelSize \[IN\]**: Size of the model data.  
* **modelType \[OUT\]**: Returned model type.

**Limitations**:

Model memory must reside in device memory, which the user must manage and release.

---

#### axclrtEngineGetModelTypeFromModelId

**axclError axclrtEngineGetModelTypeFromModelId(uint64\_t modelId, axclrtEngineModelKind \*modelType);**  
**Description**:

This function retrieves the model type based on the model **ID**.

**Parameters**:

* **modelId \[IN\]**: Model **ID**.  
* **modelType \[OUT\]**: Returned model type.

**Limitations**:

No special restrictions.

---

#### axclrtEngineGetIOInfo

**axclError axclrtEngineGetIOInfo(uint64\_t modelId, axclrtEngineIOInfo \*ioInfo);**  
**Description**:

This function retrieves the model IO information based on the model **ID**.

**Parameters**:

* **modelId \[IN\]**: Model **ID**.  
* **ioInfo \[OUT\]**: Returned **axclrtEngineIOInfo** pointer.

**Limitations**:

The user should call **axclrtEngineDestroyIOInfo** to release **axclrtEngineIOInfo** before the model **ID** is destroyed.

---

#### axclrtEngineDestroyIOInfo

**axclError axclrtEngineDestroyIOInfo(axclrtEngineIOInfo ioInfo);**  
**Description**:

This function destroys data of type **axclrtEngineIOInfo**.

**Parameters**:

* **ioInfo \[IN\]**: **axclrtEngineIOInfo** pointer.

**Limitations**:

No special restrictions.

---

#### axclrtEngineGetShapeGroupsCount

**axclError axclrtEngineGetShapeGroupsCount(axclrtEngineIOInfo ioInfo, int32\_t \*count);**  
**Description**:

This function retrieves the number of IO shape groups.

**Parameters**:

* **ioInfo \[IN\]**: **axclrtEngineIOInfo** pointer.  
* **count \[OUT\]**: Number of shape groups.

**Limitations**:

The Pulsar2 toolchain can specify multiple shapes during model conversion. Standard models typically have only one shape, so calling this function for normally converted models is unnecessary.

---

#### axclrtEngineGetNumInputs

**uint32\_t axclrtEngineGetNumInputs(axclrtEngineIOInfo ioInfo);**  
**Description**:

This function retrieves the number of model inputs from **axclrtEngineIOInfo**.

**Parameters**:

* **ioInfo \[IN\]**: **axclrtEngineIOInfo** pointer.

**Limitations**:

No special restrictions.

---

#### axclrtEngineGetNumOutputs

**uint32\_t axclrtEngineGetNumOutputs(axclrtEngineIOInfo ioInfo);**  
**Description**:

This function retrieves the number of model outputs from **axclrtEngineIOInfo**.

**Parameters**:

* **ioInfo \[IN\]**: **axclrtEngineIOInfo** pointer.

**Limitations**:

No special restrictions.

---

#### axclrtEngineGetInputSizeByIndex

**uint64\_t axclrtEngineGetInputSizeByIndex(axclrtEngineIOInfo ioInfo, uint32\_t group, uint32\_t index);**  
**Description**:

This function retrieves the size of a specific input based on **axclrtEngineIOInfo**.

**Parameters**:

* **ioInfo \[IN\]**: **axclrtEngineIOInfo** pointer.  
* **group \[IN\]**: Input shape group index.  
* **index \[IN\]**: Index of the input whose size is to be retrieved, starting from 0\.

**Limitations**:

No special restrictions.

---

#### axclrtEngineGetOutputSizeByIndex

**uint64\_t axclrtEngineGetOutputSizeByIndex(axclrtEngineIOInfo ioInfo, uint32\_t group, uint32\_t index);**  
**Description**:

This function retrieves the size of a specific output based on **axclrtEngineIOInfo**.

**Parameters**:

* **ioInfo \[IN\]**: **axclrtEngineIOInfo** pointer.  
* **group \[IN\]**: Output shape group index.  
* **index \[IN\]**: Index of the output whose size is to be retrieved, starting from 0\.

**Limitations**:

No special restrictions.

---

#### axclrtEngineGetInputNameByIndex

**const char \*axclrtEngineGetInputNameByIndex(axclrtEngineIOInfo ioInfo, uint32\_t index);**  
**Description**:

This function retrieves the name of a specific input.

**Parameters**:

* **ioInfo \[IN\]**: **axclrtEngineIOInfo** pointer.  
* **index \[IN\]**: Input IO index.

**Limitations**:

The returned input tensor name has the same lifecycle as **ioInfo**.

---

#### axclrtEngineGetOutputNameByIndex

**const char \*axclrtEngineGetOutputNameByIndex(axclrtEngineIOInfo ioInfo, uint32\_t index);**  
**Description**:

This function retrieves the name of a specific output.

**Parameters**:

* **ioInfo \[IN\]**: **axclrtEngineIOInfo** pointer.  
* **index \[IN\]**: Output IO index.

**Limitations**:

The returned output tensor name has the same lifecycle as **ioInfo**.

---

#### axclrtEngineGetInputIndexByName

**int32\_t axclrtEngineGetInputIndexByName(axclrtEngineIOInfo ioInfo, const char \*name);**  
**Description**:

This function retrieves the input index based on the name of the input tensor.

**Parameters**:

* **ioInfo \[IN\]**: Model description.  
* **name \[IN\]**: Input tensor name.

**Limitations**:

No special restrictions.

---

#### axclrtEngineGetOutputIndexByName

**int32\_t axclrtEngineGetOutputIndexByName(axclrtEngineIOInfo ioInfo, const char \*name);**  
**Description**:

This function retrieves the output index based on the name of the output tensor.

**Parameters**:

* **ioInfo \[IN\]**: Model description.  
* **name \[IN\]**: Output tensor name.

**Limitations**:

No special restrictions.

---

#### axclrtEngineGetInputDims

**axclError axclrtEngineGetInputDims(axclrtEngineIOInfo ioInfo, uint32\_t group, uint32\_t index, axclrtEngineIODims \*dims);**  
**Description**:

This function retrieves the dimension information of a specified input.

**Parameters**:

* **ioInfo \[IN\]**: **axclrtEngineIOInfo** pointer.  
* **group \[IN\]**: Input shape group index.  
* **index \[IN\]**: Input tensor index.  
* **dims \[OUT\]**: Returned dimension information.

**Limitations**:

The storage space for **axclrtEngineIODims** is allocated by the user, and should be released before **axclrtEngineIOInfo** is destroyed.

---

#### axclrtEngineGetOutputDims

**axclError axclrtEngineGetOutputDims(axclrtEngineIOInfo ioInfo, uint32\_t group, uint32\_t index, axclrtEngineIODims \*dims);**  
**Description**:

This function retrieves the dimension information of a specified output.

**Parameters**:

* **ioInfo \[IN\]**: **axclrtEngineIOInfo** pointer.  
* **group \[IN\]**: Output shape group index.  
* **index \[IN\]**: Output tensor index.  
* **dims \[OUT\]**: Returned dimension information.

**Limitations**:

The storage space for **axclrtEngineIODims** is allocated by the user, and should be released before **axclrtEngineIOInfo** is destroyed.

---

#### axclrtEngineCreateIO

**axclError axclrtEngineCreateIO(axclrtEngineIOInfo ioInfo, axclrtEngineIO \*io);**  
**Description**:

This function creates data of type **axclrtEngineIO**.

**Parameters**:

* **ioInfo \[IN\]**: **axclrtEngineIOInfo** pointer.  
* **io \[OUT\]**: Created **axclrtEngineIO** pointer.

**Limitations**:

The user should call **axclrtEngineDestroyIO** to release **axclrtEngineIO** before the model **ID** is destroyed.

---

#### axclrtEngineDestroyIO

**axclError axclrtEngineDestroyIO(axclrtEngineIO io);**  
**Description**:

This function destroys data of type **axclrtEngineIO**.

**Parameters**:

* **io \[IN\]**: The **axclrtEngineIO** pointer to be destroyed.

**Limitations**:

No special restrictions.

---

#### axclrtEngineSetInputBufferByIndex

**axclError axclrtEngineSetInputBufferByIndex(axclrtEngineIO io, uint32\_t index, const void \*dataBuffer, uint64\_t size);**  
**Description**:

This function sets the input data buffer by IO index.

**Parameters**:

* **io \[IN\]**: Address of the **axclrtEngineIO** data buffer.  
* **index \[IN\]**: Input tensor index.  
* **dataBuffer \[IN\]**: Address of the data buffer to add.  
* **size \[IN\]**: Size of the data buffer.

**Limitations**:

The data buffer must be in device memory, and the user is responsible for managing and releasing it.

---

#### axclrtEngineSetOutputBufferByIndex

**axclError axclrtEngineSetOutputBufferByIndex(axclrtEngineIO io, uint32\_t index, const void \*dataBuffer, uint64\_t size);**  
**Description**:

This function sets the output data buffer by IO index.

**Parameters**:

* **io \[IN\]**: Address of the **axclrtEngineIO** data buffer.  
* **index \[IN\]**: Output tensor index.  
* **dataBuffer \[IN\]**: Address of the data buffer to add.  
* **size \[IN\]**: Size of the data buffer.

**Limitations**:

The data buffer must be in device memory, and the user is responsible for managing and releasing it.

---

#### axclrtEngineSetInputBufferByName

**axclError axclrtEngineSetInputBufferByName(axclrtEngineIO io, const char \*name, const void \*dataBuffer, uint64\_t size);**  
**Description**:

This function sets the input data buffer by IO name.

**Parameters**:

* **io \[IN\]**: Address of the **axclrtEngineIO** data buffer.  
* **name \[IN\]**: Input tensor name.  
* **dataBuffer \[IN\]**: Address of the data buffer to add.  
* **size \[IN\]**: Size of the data buffer.

**Limitations**:

The data buffer must be in device memory, and the user is responsible for managing and releasing it.

---

#### axclrtEngineSetOutputBufferByName

**axclError axclrtEngineSetOutputBufferByName(axclrtEngineIO io, const char \*name, const void \*dataBuffer, uint64\_t size);**  
**Description**:

This function sets the output data buffer by IO name.

**Parameters**:

* **io \[IN\]**: Address of the **axclrtEngineIO** data buffer.  
* **name \[IN\]**: Output tensor name.  
* **dataBuffer \[IN\]**: Address of the data buffer to add.  
* **size \[IN\]**: Size of the data buffer.

**Limitations**:

The data buffer must be in device memory, and the user is responsible for managing and releasing it.

---

#### axclrtEngineGetInputBufferByIndex

**axclError axclrtEngineGetInputBufferByIndex(axclrtEngineIO io, uint32\_t index, void \*\*dataBuffer, uint64\_t \*size);**  
**Description**:

This function retrieves the input data buffer by IO index.

**Parameters**:

* **io \[IN\]**: Address of the **axclrtEngineIO** data buffer.  
* **index \[IN\]**: Input tensor index.  
* **dataBuffer \[OUT\]**: Address of the data buffer.  
* **size \[IN\]**: Size of the data buffer.

**Limitations**:

The data buffer must be in device memory, and the user is responsible for managing and releasing it.

---

#### axclrtEngineGetOutputBufferByIndex

**axclError axclrtEngineGetOutputBufferByIndex(axclrtEngineIO io, uint32\_t index, void \*\*dataBuffer, uint64\_t \*size);**  
**Description**:

This function retrieves the output data buffer by IO index.

**Parameters**:

* **io \[IN\]**: Address of the **axclrtEngineIO** data buffer.  
* **index \[IN\]**: Output tensor index.  
* **dataBuffer \[OUT\]**: Address of the data buffer.  
* **size \[IN\]**: Size of the data buffer.

**Limitations**:

The data buffer must be in device memory, and the user is responsible for managing and releasing it.

---

#### axclrtEngineGetInputBufferByName

**axclError axclrtEngineGetInputBufferByName(axclrtEngineIO io, const char \*name, void \*\*dataBuffer, uint64\_t \*size);**  
**Description**:

This function retrieves the input data buffer by IO name.

**Parameters**:

* **io \[IN\]**: Address of the **axclrtEngineIO** data buffer.  
* **name \[IN\]**: Input tensor name.  
* **dataBuffer \[OUT\]**: Address of the data buffer.

**Limitations**:

The data buffer must be in device memory, and the user is responsible for managing and releasing it.

---

#### axclrtEngineGetOutputBufferByName

**axclError axclrtEngineGetOutputBufferByName(axclrtEngineIO io, const char \*name, void \*\*dataBuffer, uint64\_t \*size);**  
**Description**:

This function retrieves the output data buffer by IO name.

**Parameters**:

* **io \[IN\]**: Address of the **axclrtEngineIO** data buffer.  
* **name \[IN\]**: Output tensor name.  
* **dataBuffer \[OUT\]**: Address of the data buffer.

**Limitations**:

The data buffer must be in device memory, and the user is responsible for managing and releasing it.

---

#### axclrtEngineSetDynamicBatchSize

**axclError axclrtEngineSetDynamicBatchSize(axclrtEngineIO io, uint32\_t batchSize);**  
**Description**:

This function sets the number of images processed at one time in a dynamic batching scenario.

**Parameters**:

* **io \[IN\]**: Model inference IO.  
* **batchSize \[IN\]**: Number of images processed at one time.

**Limitations**:

No special restrictions.

---

#### axclrtEngineCreateContext

**axclError axclrtEngineCreateContext(uint64\_t modelId, uint64\_t \*contextId);**  
**Description**:

This function creates a model runtime context for the given model **ID**.

**Parameters**:

* **modelId \[IN\]**: Model **ID**.  
* **contextId \[OUT\]**: Created context **ID**.

**Limitations**:

A model **ID** can have multiple runtime contexts, each running with its own settings and memory space.

---

#### axclrtEngineExecute

**axclError axclrtEngineExecute(uint64\_t modelId, uint64\_t contextId, uint32\_t group, axclrtEngineIO io);**  
**Description**:

This function performs synchronous inference for the model until the inference result is returned.

**Parameters**:

* **modelId \[IN\]**: Model **ID**.  
* **contextId \[IN\]**: Model inference context.  
* **group \[IN\]**: Model shape group index.  
* **io \[IN\]**: Model inference IO.

**Limitations**:

No special restrictions.

---

#### axclrtEngineExecuteAsync

**axclError axclrtEngineExecuteAsync(uint64\_t modelId, uint64\_t contextId, uint32\_t group, axclrtEngineIO io, axclrtStream stream);**  
**Description**:

This function performs asynchronous inference for the model.

**Parameters**:

* **modelId \[IN\]**: Model **ID**.  
* **contextId \[IN\]**: Model inference context.  
* **group \[IN\]**: Model shape group index.  
* **io \[IN\]**: Model inference IO.  
* **stream \[IN\]**: Stream.

**Limitations**:

No special restrictions.

## native

* The AXCL NATIVE module supports the SYS, VDEC, VENC, IVPS, DMADIM, ENGINE, and IVE modules.  
* The AXCL NATIVE API parameters are exactly the same as those of the AX SDK API, the only difference being that the function names change from the original AX prefix to AXCL.  
  Example:

**AX\_S32 AXCL\_SYS\_Init(AX\_VOID);**  
**AX\_S32 AXCL\_SYS\_Deinit(AX\_VOID);**

**/\* CMM API \*/**  
**AX\_S32 AXCL\_SYS\_MemAlloc(AX\_U64 \*phyaddr, AX\_VOID \*\*pviraddr, AX\_U32 size, AX\_U32 align, const AX\_S8 \*token);**  
**AX\_S32 AXCL\_SYS\_MemAllocCached(AX\_U64 \*phyaddr, AX\_VOID \*\*pviraddr, AX\_U32 size, AX\_U32 align, const AX\_S8 \*token);**  
**AX\_S32 AXCL\_SYS\_MemFree(AX\_U64 phyaddr, AX\_VOID \*pviraddr);**

**...**

**AX\_S32 AXCL\_VDEC\_Init(const AX\_VDEC\_MOD\_ATTR\_T \*pstModAttr);**  
**AX\_S32 AXCL\_VDEC\_Deinit(AX\_VOID);**

**AX\_S32 AXCL\_VDEC\_ExtractStreamHeaderInfo(const AX\_VDEC\_STREAM\_T \*pstStreamBuf, AX\_PAYLOAD\_TYPE\_E enVideoType,**  
                                         **AX\_VDEC\_BITSTREAM\_INFO\_T \*pstBitStreamInfo);**

**AX\_S32 AXCL\_VDEC\_CreateGrp(AX\_VDEC\_GRP VdGrp, const AX\_VDEC\_GRP\_ATTR\_T \*pstGrpAttr);**  
**AX\_S32 AXCL\_VDEC\_CreateGrpEx(AX\_VDEC\_GRP \*VdGrp, const AX\_VDEC\_GRP\_ATTR\_T \*pstGrpAttr);**  
**AX\_S32 AXCL\_VDEC\_DestroyGrp(AX\_VDEC\_GRP VdGrp);**

* **...**  
* Please refer to the AX SDK API documentation, such as **"AX SYS API Documentation.docx"**, **"AX VDEC API Documentation.docx"**, etc.  
* The dynamic library **.so** naming has changed from the original **libax\_xxx.so** to **libaxcl\_xxx.so**. The comparison table is as follows:

| Module | AX SDK | AXCL NATIVE SDK |
| :---: | :---: | :---: |
| SYS | libax\_sys.so | libaxcl\_sys.so |
| VDEC | libax\_vdec.so | libaxcl\_vdec.so |
| VENC | libax\_venc.so | libaxcl\_venc.so |
| IVPS | libax\_ivps.so | libaxcl\_ivps.so |
| DMADIM | libax\_dmadim.so | libaxcl\_dmadim.so |
| ENGINE | libax\_engine.so | libaxcl\_engine.so |
| IVE | libax\_ive.so | libaxcl\_ive.so |

* Some AX SDK APIs are not supported in AXCL NATIVE. The specific list is as follows:

| Module | AXCL NATIVE API | Description |
| :---: | :---: | :---: |
| SYS | AXCL\_SYS\_EnableTimestamp |  |
|  | AXCL\_SYS\_Sleep |  |
|  | AXCL\_SYS\_WakeLock |  |
|  | AXCL\_SYS\_WakeUnlock |  |
|  | AXCL\_SYS\_RegisterEventCb |  |
|  | AXCL\_SYS\_UnregisterEventCb |  |
| VENC | AXCL\_VENC\_GetFd |  |
|  | AXCL\_VENC\_JpegGetThumbnail |  |
| IVPS | AXCL\_IVPS\_GetChnFd |  |
|  | AXCL\_IVPS\_CloseAllFd |  |
| DMADIM | AXCL\_DMADIM\_Cfg | Callback function not supported, i.e., AX\_DMADIM\_MSG\_T.pfnCallBack |
| IVE | AXCL\_IVE\_NPU\_CreateMatMulHandle |  |
|  | AX\_IVE\_NPU\_DestroyMatMulHandle |  |
|  | AX\_IVE\_NPU\_MatMul |  |

## PPL

### architecture

**libaxcl\_ppl.so** is a highly integrated module that implements typical pipeline (PPL). The architecture diagram is as follows:

**| \----------------------------- |**  
**| application                   |**  
**| \----------------------------- |**  
**| libaxcl\_ppl.so                |**  
**| \----------------------------- |**  
**| libaxcl\_lite.so               |**  
**| \----------------------------- |**  
**| axcl sdk                      |**  
**| \----------------------------- |**  
**| pcie driver                   |**  
**| \----------------------------- |**  
**Note**  
**libaxcl\_lite.so** and **libaxcl\_ppl.so** are open-source libraries which located in **axcl/sample/axclit** and **axcl/sample/ppl** directories.

#### transcode

Refer to the source code of **axcl\_transcode\_sample** which located in path: **axcl/sample/ppl/transode**.

### API

#### axcl\_ppl\_init

axcl runtime system and ppl initialization.

##### prototype

axclError axcl\_ppl\_init(const axcl\_ppl\_init\_param\* param);

##### parameter

| parameter | description | in/out |
| :---: | :---: | :---: |
| param |  | in |

**typedef enum {**  
    **AXCL\_LITE\_NONE \= 0,**  
    **AXCL\_LITE\_VDEC \= (1 \<\< 0),**  
    **AXCL\_LITE\_VENC \= (1 \<\< 1),**  
    **AXCL\_LITE\_IVPS \= (1 \<\< 2),**  
    **AXCL\_LITE\_JDEC \= (1 \<\< 3),**  
    **AXCL\_LITE\_JENC \= (1 \<\< 4),**  
    **AXCL\_LITE\_DEFAULT \= (AXCL\_LITE\_VDEC | AXCL\_LITE\_VENC | AXCL\_LITE\_IVPS),**  
    **AXCL\_LITE\_MODULE\_BUTT**  
**} AXCLITE\_MODULE\_E;**

**typedef struct {**  
    **const char \*json; /\* axcl.json path \*/**  
    **AX\_S32 device;**  
    **AX\_U32 modules;**  
    **AX\_U32 max\_vdec\_grp;**  
    **AX\_U32 max\_venc\_thd;**  
**} axcl\_ppl\_init\_param;**

| parameter | description | in/out |
| :---: | :---: | :---: |
| json | json file path pass to **axclInit** API. | in |
| device | device id | in |
| modules | bitmask of AXCLITE\_MODULE\_E according to PPL | in |
| max\_vdec\_grp | total VDEC groups of all processes | in |
| max\_venc\_thrd | max VENC threads of each process | in |

**IMPORTANT:**

* AXCL\_PPL\_TRANSCODE: modules \= AXCL\_LITE\_DEFAULT  
* **max\_vdec\_grp** should be equal to or greater than the total number of VDEC groups across all processes. For example, if 16 processes are launched, with each process having one decoder, **max\_vdec\_grp** should be set to at least 16\.  
* **max\_venc\_thrd** usually be configured as same as the total VENC channels of each process.

##### return

0 (AXCL\_SUCC) if success, otherwise failure.

#### axcl\_ppl\_deinit

axcl runtime system and ppl deinitialization.

##### prototype

axclError axcl\_ppl\_deinit();

##### return

0 (AXCL\_SUCC) if success, otherwise failure.

#### axcl\_ppl\_create

create ppl.

##### prototype

axclError axcl\_ppl\_create(axcl\_ppl\* ppl, const axcl\_ppl\_param\* param);

##### parameter

| parameter | description | in/out |
| :---: | :---: | :---: |
| ppl | ppl handle created | out |
| param | parameters related to specified ppl | in |

**typedef enum {**  
    **AXCL\_PPL\_TRANSCODE \= 0, /\* VDEC \-\> IVPS \-\>VENC \*/**  
    **AXCL\_PPL\_BUTT**  
**} axcl\_ppl\_type;**

**typedef struct {**  
    **axcl\_ppl\_type ppl;**  
    **void \*param;**  
**} axcl\_ppl\_param;**  
**AXCL\_PPL\_TRANSCODE** parameters as shown as follows:

**typedef AX\_VENC\_STREAM\_T axcl\_ppl\_encoded\_stream;**  
**typedef void (\*axcl\_ppl\_encoded\_stream\_callback\_func)(axcl\_ppl ppl, const axcl\_ppl\_encoded\_stream \*stream, AX\_U64 userdata);**

**typedef struct {**  
    **axcl\_ppl\_transcode\_vdec\_attr vdec;**  
    **axcl\_ppl\_transcode\_venc\_attr venc;**  
    **axcl\_ppl\_encoded\_stream\_callback\_func cb;**  
    **AX\_U64 userdata;**  
**} axcl\_ppl\_transcode\_param;**

| parameter | description | in/out |
| :---: | :---: | :---: |
| vdec | decoder attribute | in |
| venc | encoder attribute | in |
| cb | callback function to receive encoded nalu frame data | in |
| userdata | userdata bypass to axcl\_ppl\_encoded\_stream\_callback\_func | in |

**Warning**  
Avoid high-latency processing inside the *axcl\_ppl\_encoded\_stream\_callback\_func* function  
**typedef struct {**  
    **AX\_PAYLOAD\_TYPE\_E payload;**  
    **AX\_U32 width;**  
    **AX\_U32 height;**  
    **AX\_VDEC\_OUTPUT\_ORDER\_E output\_order;**  
    **AX\_VDEC\_DISPLAY\_MODE\_E display\_mode;**  
**} axcl\_ppl\_transcode\_vdec\_attr;**

| parameter | description | in/out |
| :---: | :---: | :---: |
| payload | PT\_H2644 \\ PT\_H265 | in |
| width | max. width of input stream | in |
| height | max. height of input stream | in |
| output\_order | AX\_VDEC\_OUTPUT\_ORDER\_DISP \\ AX\_VDEC\_OUTPUT\_ORDER\_DEC | in |
| display\_mode | AX\_VDEC\_DISPLAY\_MODE\_PREVIEW \\ AX\_VDEC\_DISPLAY\_MODE\_PLAYBACK | in |

Important:

* **output\_order**:  
  * If decode sequence is same as display sequence such as IP stream, recommend to AX\_VDEC\_OUTPUT\_ORDER\_DEC to save memory.  
  * If decode sequence is different to display sequence such as IPB stream, set AX\_VDEC\_OUTPUT\_ORDER\_DISP.  
* **display\_mode**  
  * AX\_VDEC\_DISPLAY\_MODE\_PREVIEW: preview mode which frame dropping is allowed typically for RTSP stream... etc.  
  * AX\_VDEC\_DISPLAY\_MODE\_PLAYBACK: playback mode which frame dropping is not forbidden typically for local stream file.

**typedef struct {**  
    **AX\_PAYLOAD\_TYPE\_E payload;**  
    **AX\_U32 width;**  
    **AX\_U32 height;**  
    **AX\_VENC\_PROFILE\_E profile;**  
    **AX\_VENC\_LEVEL\_E level;**  
    **AX\_VENC\_TIER\_E tile;**  
    **AX\_VENC\_RC\_ATTR\_T rc;**  
    **AX\_VENC\_GOP\_ATTR\_T gop;**  
**} axcl\_ppl\_transcode\_venc\_attr;**

| parameter | description | in/out |
| :---: | :---: | :---: |
| payload | PT\_H264 \\ PT\_H265 | in |
| width | output width of encoded nalu frame | in |
| height | output height of encoded nalu frame | in |
| profile | h264 or h265 profile | in |
| level | h264 or h265 level | in |
| tile | tile | in |
| rc | rate control settings | in |
| gop | gop settings | in |

##### return

0 (AXCL\_SUCC) if success, otherwise failure.

#### axcl\_ppl\_destroy

destroy ppl.

##### prototype

axclError axcl\_ppl\_destroy(axcl\_ppl ppl)

##### parameter

| parameter | description | in/out |
| :---: | :---: | :---: |
| ppl | ppl handle created | in |

#### return

0 (AXCL\_SUCC) if success, otherwise failure.

#### axcl\_ppl\_start

start ppl.

##### prototype

axclError axcl\_ppl\_start(axcl\_ppl ppl);

##### parameter

| parameter | description | in/out |
| :---: | :---: | :---: |
| ppl | ppl handle created | in |

##### return

0 (AXCL\_SUCC) if success, otherwise failure.

#### axcl\_ppl\_stop

stop ppl.

##### prototype

axclError axcl\_ppl\_stop(axcl\_ppl ppl);

##### parameter

| parameter | description | in/out |
| :---: | :---: | :---: |
| ppl | ppl handle created | in |

##### return

0 (AXCL\_SUCC) if success, otherwise failure.

#### axcl\_ppl\_send\_stream

send nalu frame to ppl.

##### prototype

axclError axcl\_ppl\_send\_stream(axcl\_ppl ppl, const axcl\_ppl\_input\_stream\* stream, AX\_S32 timeout);

##### parameter

| parameter | description | in/out |
| :---: | :---: | :---: |
| ppl | ppl handle created | in |
| stream | nalu frame | in |
| timeout | timeout in milliseconds | in |

**typedef struct {**  
    **AX\_U8 \*nalu;**  
    **AX\_U32 nalu\_len;**  
    **AX\_U64 pts;**  
    **AX\_U64 userdata;**  
**} axcl\_ppl\_input\_stream;**

| parameter | description | in/out |
| :---: | :---: | :---: |
| nalu | pointer to nalu frame data | in |
| nalu\_len | bytes of nalu frame data | in |
| pts | timestamp of nalu frame | in |
| userdata | userdata bypass to ***axcl\_ppl\_encoded\_stream.stPack.u64UserData*** | in |

##### return

0 (AXCL\_SUCC) if success, otherwise failure.

#### axcl\_ppl\_get\_attr

get attribute of ppl.

##### prototype

axclError axcl\_ppl\_get\_attr(axcl\_ppl ppl, const char\* name, void\* attr);

##### parameter

| parameter | description | in/out |
| :---: | :---: | :---: |
| ppl | ppl handle created | in |
| name | attribute name | in |
| attr | attribute value | out |

**/\*\***  
 **\*            name                                     attr type        default**  
 **\*  axcl.ppl.id                             \[R  \]       int32\_t                            increment \+1 for each axcl\_ppl\_create**  
 **\***  
 **\*  axcl.ppl.transcode.vdec.grp             \[R  \]       int32\_t                            allocated by ax\_vdec.ko**  
 **\*  axcl.ppl.transcode.ivps.grp             \[R  \]       int32\_t                            allocated by ax\_ivps.ko**  
 **\*  axcl.ppl.transcode.venc.chn             \[R  \]       int32\_t                            allocated by ax\_venc.ko**  
 **\***  
 **\*  the following attributes take effect BEFORE the axcl\_ppl\_create function is called:**  
 **\*  axcl.ppl.transcode.vdec.blk.cnt         \[R/W\]       uint32\_t          8                depend on stream DPB size and decode mode**  
 **\*  axcl.ppl.transcode.vdec.out.depth       \[R/W\]       uint32\_t          4                out fifo depth**  
 **\*  axcl.ppl.transcode.ivps.in.depth        \[R/W\]       uint32\_t          4                in fifo depth**  
 **\*  axcl.ppl.transcode.ivps.out.depth       \[R  \]       uint32\_t          0                out fifo depth**  
 **\*  axcl.ppl.transcode.ivps.blk.cnt         \[R/W\]       uint32\_t          4**  
 **\*  axcl.ppl.transcode.ivps.engine          \[R/W\]       uint32\_t   AX\_IVPS\_ENGINE\_VPP      AX\_IVPS\_ENGINE\_VPP|AX\_IVPS\_ENGINE\_VGP|AX\_IVPS\_ENGINE\_TDP**  
 **\*  axcl.ppl.transcode.venc.in.depth        \[R/W\]       uint32\_t          4                in fifo depth**  
 **\*  axcl.ppl.transcode.venc.out.depth       \[R/W\]       uint32\_t          4                out fifo depth**  
 **\*/**  
**Important**  
**axcl.ppl.transcode.vdec.blk.cnt**: blk count is related to the DBP size of input stream, recommend to set dbp \+ 1\.

##### return

0 (AXCL\_SUCC) if success, otherwise failure.

#### axcl\_ppl\_set\_attr

set attribute of ppl.

##### prototype

axclError axcl\_ppl\_set\_attr(axcl\_ppl ppl, const char\* name, const void\* attr);

##### parameter

| parameter | description | in/out |
| :---: | :---: | :---: |
| ppl | ppl handle created | in |
| name | attribute name, refer to ***axcl\_ppl\_get\_attr*** | in |
| attr | attribute value | in |

##### return

0 (AXCL\_SUCC) if success, otherwise failure.

## Error Codes

### Definition

**typedef int32\_t axclError;**

**typedef enum {**  
    **AXCL\_SUCC                   \= 0x00,**  
    **AXCL\_FAIL                   \= 0x01,**  
    **AXCL\_ERR\_UNKNOWN            \= AXCL\_FAIL,**  
    **AXCL\_ERR\_NULL\_POINTER       \= 0x02,**  
    **AXCL\_ERR\_ILLEGAL\_PARAM      \= 0x03,**  
    **AXCL\_ERR\_UNSUPPORT          \= 0x04,**  
    **AXCL\_ERR\_TIMEOUT            \= 0x05,**  
    **AXCL\_ERR\_BUSY               \= 0x06,**  
    **AXCL\_ERR\_NO\_MEMORY          \= 0x07,**  
    **AXCL\_ERR\_ENCODE             \= 0x08,**  
    **AXCL\_ERR\_DECODE             \= 0x09,**  
    **AXCL\_ERR\_UNEXPECT\_RESPONSE  \= 0x0A,**  
    **AXCL\_ERR\_OPEN               \= 0x0B,**  
    **AXCL\_ERR\_EXECUTE\_FAIL       \= 0x0C,**

    **AXCL\_ERR\_BUTT               \= 0x7F**  
**} AXCL\_ERROR\_E;**

**\#define AX\_ID\_AXCL           (0x30)**

**/\* module \*/**  
**\#define AXCL\_RUNTIME         (0x00)**  
**\#define AXCL\_NATIVE          (0x01)**  
**\#define AXCL\_LITE            (0x02)**

**/\* runtime sub module \*/**  
**\#define AXCL\_RUNTIME\_DEVICE  (0x01)**  
**\#define AXCL\_RUNTIME\_CONTEXT (0x02)**  
**\#define AXCL\_RUNTIME\_STREAM  (0x03)**  
**\#define AXCL\_RUNTIME\_TASK    (0x04)**  
**\#define AXCL\_RUNTIME\_MEMORY  (0x05)**  
**\#define AXCL\_RUNTIME\_CONFIG  (0x06)**  
**\#define AXCL\_RUNTIME\_ENGINE  (0x07)**  
**\#define AXCL\_RUNTIME\_SYSTEM  (0x08)**

**/\*\***  
 **\* |---------------------------------------------------------|**  
 **\* | |   MODULE    |  AX\_ID\_AXCL | SUB\_MODULE  |    ERR\_ID   |**  
 **\* |1|--- 7bits \---|--- 8bits \---|--- 8bits \---|--- 8bits \---|**  
 **\*\*/**  
**\#define AXCL\_DEF\_ERR(module, sub, errid) \\**  
    **((axclError)((0x80000000L) | (((module) & 0x7F) \<\< 24\) | ((AX\_ID\_AXCL) \<\< 16 ) | ((sub) \<\< 8\) | (errid)))**

**\#define AXCL\_DEF\_RUNTIME\_ERR(sub, errid)    AXCL\_DEF\_ERR(AXCL\_RUNTIME, (sub), (errid))**  
**\#define AXCL\_DEF\_NATIVE\_ERR(sub,  errid)    AXCL\_DEF\_ERR(AXCL\_NATIVE,  (sub), (errid))**  
**\#define AXCL\_DEF\_LITE\_ERR(sub,    errid)    AXCL\_DEF\_ERR(AXCL\_LITE,    (sub), (errid))**  
Note:

Error codes are divided into two types: **AXCL Runtime Library** and **AX NATIVE SDK** error codes, distinguished by the third byte of **axclError**.  
If the third byte is equal to **AX\_ID\_AXCL (0x30)**, it indicates an **AXCL Runtime Library** error code; otherwise, it indicates a Device-side **AX NATIVE SDK** module error code passed through to the HOST side.

* **AXCL Runtime Library error codes**: Refer to the **axcl\_rt\_xxx.h** header file.  
* **Device NATIVE SDK error codes** are passed directly to the HOST side: Refer to the *"AX Software Error Code Documentation"*.

---

# **AXCL-SMI**

## Overview

The AXCL-SMI (System Management Interface) tool is used for device information collection, device configuration, and other functions. It supports collecting the following device information:

* Hardware device model  
* Firmware version  
* Driver version  
* Device utilization  
* Memory usage  
* Device chip junction temperature  
* Other information

## Instructions

### Quick Start

After the AXCL driver package is correctly installed, AXCL-SMI is available. Run **axcl-smi** directly to display the output as follows:

**\+------------------------------------------------------------------------------------------------+**  
**| AXCL-SMI  V3.6.4\_20250805020145                                  Driver  V3.6.4\_20250805020145 |**  
**\+-----------------------------------------+--------------+---------------------------------------+**  
**| Card  Name                     Firmware                                                          | Bus-Id       | Memory-Usage           |**  
**| Fan   Temp                Pwr:Usage/Cap                                                          | CPU      NPU | CMM-Usage              |**  
**| \=========================================+==============+======================================= |**  
**| 0  AX650N                     V3.6.4                                                             | 0001:01:00.0 | 149 MiB /      945 MiB |**  
**| \--   41C                      \-- / \--                                                            | 1%        0% | 18 MiB /     7040 MiB  |**  
**\+-----------------------------------------+--------------+---------------------------------------+**

**\+------------------------------------------------------------------------------------------------+**  
**| Processes:                                                                                       |**  
**| Card      PID  Process Name                                                   NPU Memory Usage   |**  
**| \================================================================================================ |**  
**Field Description**

| Field | Description | Field | Description |
| :---: | :---: | :---: | :---: |
| Card | Device index number — note: not the PCIe device number | Bus-Id | Device Bus ID |
| Name | Device name | CPU | Average CPU utilization |
| Fan | Fan speed ratio (not supported) | NPU | Average NPU utilization |
| Temp | Chip junction temperature (Tj) | Memory-Usage | System memory: used / total |
| Firmware | Device firmware version | CMM-Usage | Media memory: used / total |
| Pwr: Usage/Cap | Power consumption (not supported) |  |  |
| PID | Host process PID |  |  |
| Process Name | Host process name |  |  |
| NPU Memory Usage | CMM memory used by NPU on the device |  |  |

**Note**  
See FAQ [DDR Bandwidth](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/en/m5_llm_8850_faq#ddr-bandwidth) and [NPU Utilization](https://docs.m5stack.com/en/guide/ai_accelerator/llm-8850/en/m5_llm_8850_faq#npu-utilization) to understand how to get detailed DDR and NPU utilization.

### Help (-h) & Version (-v)

**axcl-smi \-h** will show the help information

**m5stack@raspberrypi5:\~ $ axcl-smi \-h**  
**usage: axcl-smi \[\<command\> \[\<args\>\]\] \[--device\] \[--version\] \[--help\]**

**axcl-smi System Management Interface V3.6.3\_20250722020142**

**Commands**  
    **info                                    Show device information**  
        **\--temp                                  Show SoC temperature**  
        **\--mem                                   Show memory usage**  
        **\--cmm                                   Show CMM usage**  
        **\--cpu                                   Show CPU usage**  
        **\--npu                                   Show NPU usage**  
    **proc                                    cat device proc**  
        **\--vdec                                  cat /proc/ax\_proc/vdec**  
        **\--venc                                  cat /proc/ax\_proc/venc**  
        **\--jenc                                  cat /proc/ax\_proc/jenc**  
        **\--ivps                                  cat /proc/ax\_proc/ivps**  
        **\--rgn                                   cat /proc/ax\_proc/rgn**  
        **\--ive                                   cat /proc/ax\_proc/ive**  
        **\--pool                                  cat /proc/ax\_proc/pool**  
        **\--link                                  cat /proc/ax\_proc/link\_table**  
        **\--cmm                                   cat /proc/ax\_proc/mem\_cmm\_info**  
    **set                                     Set**  
        **\-f\[MHz\], \--freq=\[MHz\]                   Set CPU frequency in MHz. One of: 1200000, 1400000, 1700000**  
    **log                                     Dump logs from device**  
        **\-t\[mask\], \--type\=\[mask\]                 Specifies which logs to dump by a combination (bitwise OR) value of below:**  
                                                  **\-1: all (default) 0x01: daemon 0x02: worker 0x10: syslog 0x20: kernel**  
        **\-o\[path\], \--output=\[path\]               Specifies the path to save dump logs (default: ./)**  
    **sh                                      Execute a shell command**  
        **cmd                                     Shell command**  
        **args...                                 Shell command arguments**  
    **reboot                                  reboot device**  
**\-d, \--device                            Card index \[0, connected cards number \- 1\]**  
**\-v, \--version                           Show axcl-smi version**  
**\-h, \--help                              Show this help menu**

**axcl-smi \-v** will show the AXCL-SMI version

**m5stack@raspberrypi5:\~ $ axcl-smi \-v**  
**AXCL-SMI V3.6.3\_20250722020142 BUILD: Jul 22 2025 02:30:24**

### Options

#### Device ID (-d, \--device)

**\-d, \--device                             Card index \[0, connected cards number \- 1\]**  
**\[-d, \--device\]** specifies the device index; range is \[0, number of connected devices \- 1\]. **Default is device 0**.

### Info Query (info)

**axcl-smi info** displays detailed device information. Supported subcommands are:

| Subcommand | Description |
| :---: | :---: |
| \--temp | Show chip junction temperature in Celsius x1000. |
| \--mem | Show detailed system memory usage. |
| \--cmm | Show media memory usage. For more detailed media memory info, run **axcl-smi sh cat /proc/ax\_proc/mem\_cmm\_info \-d xx** (xx is the PCIe device number). |
| \--cpu | Show CPU utilization. |
| \--npu | Show NPU utilization. |

**Example**: Query media memory usage for device index 0:

**m5stack@raspberrypi5:\~ $ axcl-smi info \--cmm \-d 0**  
**Device ID           : 1 (0x1)**  
**CMM Total           :  7208960 KiB**  
**CMM Used            :    18876 KiB**  
**CMM Remain          :  7190084 kiB**

### PROC Query (proc)

**axcl-smi proc** queries device module proc info. Supported subcommands are:

| Subcommand | Description |
| :---: | :---: |
| \--vdec | Query VDEC module proc info (**cat /proc/ax\_proc/vdec**) |
| \--venc | Query VENC module proc info (**cat /proc/ax\_proc/venc**) |
| \--jenc | Query JENC module proc info (**cat /proc/ax\_proc/jenc**) |
| \--ivps | Query IVPS module proc info (**cat /proc/ax\_proc/ivps**) |
| \--rgn | Query RGN module proc info (**cat /proc/ax\_proc/rgn**) |
| \--ive | Query IVE module proc info (**cat /proc/ax\_proc/ive**) |
| \--pool | Query POOL module proc info (**cat /proc/ax\_proc/pool**) |
| \--link | Query LINK module proc info (**cat /proc/ax\_proc/link\_table**) |
| \--cmm | Query CMM module proc info (**cat /proc/ax\_proc/mem\_cmm\_info**) |

**Example**: Query VENC proc info for device 0

**m5stack@raspberrypi5:\~ $ axcl-smi proc \--venc \-d 0**  
**\-------- VENC VERSION \------------------------**  
**\[Axera version\]: ax\_venc V3.6.3\_20250722020142 Jul 22 2025 02:22:04 JK**

**\-------- MODULE PARAM \------------------------**  
**MaxChnNum   MaxRoiNum   MaxProcNum**  
**64          8           32**

### Parameter Settings (set)

**axcl-smi set** configures the device. Supported subcommands are:

| Subcommand | Description |
| :---: | :---: |
| \-f \[MHz\], \--freq=\[MHz\] | Set device CPU frequency. Supported values: 1200000, 1400000, 1700000 MHz. |

**Example**: Set CPU frequency of device index 0 to 1200MHz

**m5stack@raspberrypi5:\~ $ axcl-smi set \-f 1200000 \-d 0**  
**set cpu frequency 1200000 to device 1 succeed.**

### Download Logs (log)

**axcl-smi log** downloads device log files to the host side. Supported parameters:

| Parameter | Description |
| :---: | :---: |
| \-t \[mask\], \--type=\[mask\] | Specifies log types to download. Device-side log types: \-1: all logs 0x01: daemon 0x02: worker 0x10: syslog 0x20: kernel log Recommended: **\-1** to download all logs |
| \-o \[path\], \--output=\[path\] | Specifies save path for logs, supports absolute/relative paths, default is current directory. Directory must have write permissions. |

**Example**: Download all logs from device index 0 to current directory

**m5stack@raspberrypi5:\~ $ axcl-smi log \-d 0**  
**\[2025-07-25 10:04:30.332\]\[1802\]\[C\]\[log\]\[dump\]\[73\]: log dump finished: ./dev1\_log\_20250724210251.tar.gz**

### Shell Commands (sh)

**axcl-smi sh** supports running shell commands on the device, typically used to query device module runtime proc info.

**Example**: Query CMM information for device index 0

**m5stack@raspberrypi5:\~ $ axcl-smi sh cat /proc/ax\_proc/mem\_cmm\_info \-d 0**  
**\--------------------SDK VERSION-------------------**  
**\[Axera version\]: ax\_cmm V3.6.3\_20250722020142 Jul 22 2025 02:21:25 JK**  
**\+---PARTITION: Phys(0x148000000, 0x2FFFFFFFF), Size=7208960KB(7040MB),    NAME="anonymous"**  
 **nBlock(Max=0, Cur=23, New=0, Free=0)  nbytes(Max=0B(0KB,0MB), Cur=19329024B(18876KB,18MB), New=0B(0KB,0MB), Free=0B(0KB,0MB))  Block(Max=0B(0KB,0MB), Min=0B(0KB,0MB), Avg=0B(0KB,0MB))**  
   **|-Block: phys(0x148000000, 0x148013FFF), cache \=non-cacheable, length=80KB(0MB),    name="TDP\_DEV"**  
   **...**  
**\---CMM\_USE\_INFO:**  
 **total size=7208960KB(7040MB),used=18876KB(18MB \+ 444KB),remain=7190084KB(7021MB \+ 580KB),partition\_number=1,block\_number=23**  
**Important**  
If shell command parameters contain **\-**, **\--**, **\>** etc., use double quotes, e.g., **axcl-smi sh "ls \-l" \-d 0**.  
Use shell commands cautiously when configuring the device.

### Reboot (reboot)

**axcl-smi reboot** first resets the specified device, then automatically reloads firmware. Example:

**m5stack@raspberrypi5:\~ $ axcl-smi reboot**  
**Do you want to reboot device 0 ? (y/n): y**  
