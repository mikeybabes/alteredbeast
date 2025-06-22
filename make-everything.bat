@Echo off

REM Make a single binary of the code where all data exists!

python python\merge-binaries.py Rom\epr-11907.a7 Rom\epr-11906.a5 code.bin 01
REM this little nugget generates all the data streams found in a table inside the code
REM note there are 5 of them.
python python\decode_streams.py code.bin

REM This decompresses the map data into multiple binary files.
python python\merge-binaries.py stream1high.bin stream1low.bin level1map.bin 1
python python\merge-binaries.py stream2high.bin stream2low.bin level2map.bin 1
python python\merge-binaries.py stream3high.bin stream3low.bin level3map.bin 1
python python\merge-binaries.py stream4high.bin stream4low.bin level4map.bin 1
python python\merge-binaries.py stream5high.bin stream5low.bin level5map.bin 1

REM Game has an initial palette 256 long word entries it shoves into the palette RAM
REM then there are two sets of additional enttries one which is for level 1,2,3 and another for levels 4 & 5
python python\savebit.py code.bin game_palette_555.bin 232a0 400
python python\savebit.py code.bin game_level1_2_3_extra_palette_555.bin 236a0 400
python python\savebit.py code.bin game_level4_5_extra_palette_555.bin 23aa0 400
copy /b game_palette_555.bin+game_level1_2_3_extra_palette_555.bin palettes_level1-3.bin
copy /b game_palette_555.bin+game_level4_5_extra_palette_555.bin palettes_levels4-5.bin
REM we now convert these to 8 bit r,g,b palette files for all the tools. (as we are in 2025!)
python python\palette5bit_to_8bit.py palettes_level1-3.bin palettes_level1-3.pal
python python\palette5bit_to_8bit.py palettes_levels4-5.bin palettes_level4-5.pal

REM Merge the three planes into 4 bit index coloured linear binary so 32bytes / charcter (ignore colors 8-15)
python python\bitplanes.py Rom\opr-11676.a16 Rom\opr-11675.a15 Rom\opr-11674.a14 BG1.bin

REM generate a single wide image of both planes in the game for each level 1-5
python python\map_renderer_offset.py level1map.bin BG1.bin palettes_level1-3.pal Level1
python python\map_renderer_offset.py level2map.bin BG1.bin palettes_level1-3.pal Level2
python python\map_renderer_offset.py level3map.bin BG1.bin palettes_level1-3.pal Level3
REM Note levels4 & 5 both re-programme the memory controller so the offset to the characters changes
python python\map_renderer_offset.py level4map.bin BG1.bin palettes_level4-5.pal Level4 20000
python python\map_renderer_offset.py level5map.bin BG1.bin palettes_level4-5.pal Level5 20000

REM This generates a table of all small screen images used in game title, and beast transformation
python python\tile_extractor.py code.bin misc_images 26c20 14

python python\swapbytes.py misc_images_1_20x20.bin 01
python python\swapbytes.py misc_images_2_20x20.bin 01
python python\swapbytes.py misc_images_3_20x20.bin 01
python python\swapbytes.py misc_images_4_20x20.bin 01
python python\swapbytes.py misc_images_5_20x18.bin 01
python python\swapbytes.py misc_images_6_20x18.bin 01
python python\swapbytes.py misc_images_7_24x18.bin 01
python python\swapbytes.py misc_images_8_12x18.bin 01
python python\swapbytes.py misc_images_9_14x18.bin 01
python python\swapbytes.py misc_images_10_20x15.bin 01
python python\swapbytes.py misc_images_11_10x15.bin 01
python python\swapbytes.py misc_images_12_24x13.bin 01
python python\swapbytes.py misc_images_13_20x20.bin 01
python python\swapbytes.py misc_images_14_20x20.bin 01

python python\generic_plotter.py misc_images_1_20x20.bin BG1.bin palettes_level1-3.pal tile1.png 20
python python\generic_plotter.py misc_images_2_20x20.bin BG1.bin palettes_level1-3.pal tile2.png 20
python python\generic_plotter.py misc_images_3_20x20.bin BG1.bin palettes_level1-3.pal tile3.png 20
python python\generic_plotter.py misc_images_4_20x20.bin BG1.bin palettes_level1-3.pal tile4.png 20
python python\generic_plotter.py misc_images_5_20x18.bin BG1.bin palettes_level1-3.pal tile5.png 20
python python\generic_plotter.py misc_images_6_20x18.bin BG1.bin palettes_level1-3.pal tile6.png 20
python python\generic_plotter.py misc_images_7_24x18.bin BG1.bin palettes_level1-3.pal tile7.png 24
python python\generic_plotter.py misc_images_8_12x18.bin BG1.bin palettes_level1-3.pal tile8.png 12
python python\generic_plotter.py misc_images_9_14x18.bin BG1.bin palettes_level1-3.pal tile9.png 14
python python\generic_plotter.py misc_images_10_20x15.bin BG1.bin palettes_level1-3.pal tile10.png 20
python python\generic_plotter.py misc_images_11_10x15.bin BG1.bin palettes_level1-3.pal tile11.png 10
python python\generic_plotter.py misc_images_12_24x13.bin BG1.bin palettes_level1-3.pal green_eyeball.png 24
python python\generic_plotter.py misc_images_13_20x20.bin BG1.bin palettes_level1-3.pal tile13.png 20
python python\generic_plotter.py misc_images_14_20x20.bin BG1.bin palettes_level1-3.pal tile14.png 20

python python\combine_images.py tile1.png tile2.png altered_logo.png
python python\combine_images.py tile3.png tile4.png altered_logo_bg.png
python python\combine_images.py tile5.png tile6.png tile7.png tile8.png tile9.png altered_eyeball.png
python python\combine_images.py tile11.png tile10.png blue_eyeball.png

python python\tile_extractor.py code.bin misc 28b84 2
python python\swapbytes.py misc_1_20x20.bin 01
python python\swapbytes.py misc_2_20x20.bin 01
python python\generic_plotter.py misc_1_20x20.bin BG1.bin palettes_level1-3.pal tile1.png 20
python python\generic_plotter.py misc_2_20x20.bin BG1.bin palettes_level1-3.pal tile2.png 20
python python\combine_images.py tile1.png tile2.png mural_background.png

REM when beast transforms into beast mode saved as low byte only single characters
python python\savebit.py code.bin beast_front.bin 199a 320
REM we create the high byte for character code, as they save only low byt to save memory!
REM they use $a5 in code but we only need $25 below as the top bits are priority bits
python python\dummy.py beast_high.bin 320 A5
REM interleave the two to make 16-bit character map
python python\merge-binaries.py beast_front.bin beast_high.bin beast_image_map.bin 01
python python\generic_plotter.py beast_image_map.bin BG1.bin palettes_level1-3.pal beast.png 40


REM Build up palettes for Sprites, as they are in internal table
python python\savebit.py code.bin sprite_palettes.bin 242a0 1340
REM convert the Sega16 5bit to 8bit RGB size
python python\palette5bit_to_8bit.py sprite_palettes.bin sprite_palettes.pal
REM now because the internal palettes use 14 colours, colour0 and 15 is not part of the data as it's always transparency
REM we need to expande to 16 RGB values, this just make the sprit polotting a bit easier or it's endless compares in the routine
python python\expand_palettes.py sprite_palettes.pal sprite_palettes16.pal

REM Now makeup the sprites into one big daddy sprite image
REM copy sprites from ROM folder to here, because my python script is crap!
copy rom\epr-116*.* .

REM we firstly swap the nybbles around
python python\swapnybbles.py epr-11677.b1
python python\swapnybbles.py epr-11678.b2
python python\swapnybbles.py epr-11679.b3
python python\swapnybbles.py epr-11680.b4
python python\swapnybbles.py epr-11681.b5
python python\swapnybbles.py epr-11682.b6
python python\swapnybbles.py epr-11683.b7
python python\swapnybbles.py epr-11684.b8

REM now merge them!
python python\merge-binaries.py swapped_epr-11681.b5 swapped_epr-11677.b1 sprites1.bin 1
python python\merge-binaries.py swapped_epr-11682.b6 swapped_epr-11678.b2 sprites2.bin 1
python python\merge-binaries.py swapped_epr-11683.b7 swapped_epr-11679.b3 sprites3.bin 1
python python\merge-binaries.py swapped_epr-11684.b8 swapped_epr-11680.b4 sprites4.bin 1

REM combine each into one big FO binary file
copy /b sprites1.bin+sprites2.bin+sprites3.bin+sprites4.bin all-sprites.bin
REM we keep the linear format for python sprit plotting
python python\swapnybbles.py all-sprites.bin

REM now this is some serious shit, we take the sprite data, and palette data,  and we cheat a litte!
REM I manually crated a table of the sprite number, and it's palette value. I say cheat, I actually am a lot smarter than that
REM using mame developer tools to output a watchpint on the paletee routing, and also, looking inside the disassembly.
REM we create a transparent 8-bit rgb image of all sprites with associated palette (almost perfectly)
REM also if you load both into photoshop, there is the overlay of the sprite numbers, note image is big 4k size!
python python\sprite_atlas_numbered.py code.bin swapped_all-sprites.bin sprite_palettes16.pal all_sprite_palettes.txt Altered_beast_sprites_pallette_all.png --overlay Altered_beast_sprites_palettes_all_overlay.png


REM Deletes all the working files which as not needed removed below if you want to keep them to look at.
del game_palette_555.bin
del game_level1_2_3_extra_palette_555.bin
del game_level4_5_extra_palette_555.bin
del palettes_level*.bin
del stream*.bin
del level*.bin
del tile*.png
del misc_*.bin
del beast_*.bin
del palettes_level*.pal
del code.bin
del BG1.BIN
del sprite*.*
del all-sprites.bin
del sprites*.bin
del swapped*.*
del epr*.*
