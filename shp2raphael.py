#!/usr/bin/python
#
# shp2svg
#
# simple script to convert shapefile polygons to svg

from optparse import OptionParser
import shapefile, tempita

def main():
	parser = OptionParser()

	parser.add_option("-x", "--width", action="store", type="int", dest="width",
		help="width of the svg in pixels")

	parser.add_option("-y", "--height", action="store", type="int", dest="height",
		help="height of the svg in pixels, defines destination coordinate system. you can specify width, height or both")

	parser.add_option("-i", "--in", action="store", type="string", dest="shpfile",
		help="input shapefile")

	parser.add_option("-o", "--out", action="store", type="string", dest="htmlfile",
		help="output svg file")

	parser.add_option("-a", "--attributes", action="store", type="string", dest="attrs",
		help="comma seperated list of shapefile-attributed to keep, use -A/--list-attributes to get a list of the attributed your shapefile contains")

	parser.add_option("-A", "--list-attributes", action="store_true", dest="listattrs",
		help="get a list of the attributed your shapefile contains")

	(options, args) = parser.parse_args()

	if not options.shpfile:
		parser.error('input-file is required')

	if not options.width and not options.height:
		parser.error('specify width, height or both')

	print "opening shapefile"
	shp = shapefile.Reader(options.shpfile)

	if(options.listattrs):
		print "listing attributes"
		fieldtypes = {"C": "Character", "N": "Number", "L": "Long", "D": "Date", "M": "Memo"}
		for field in shp.fields:
			print "  %s (%s)" % (field[0], fieldtypes[field[1]])
		return

	print "opening template"
	tpl = tempita.Template.from_filename("template.html")

	shapes = shp.shapes()
	print "working with %u shapes" % (len(shapes))

	print "scanning for bbox"
	bbox = [None, 0, 0, 0]
	for shape in shapes:
		if not bbox[0] or bbox[0] > shape.bbox[0]:
			bbox[0] = shape.bbox[0]
		if not bbox[1] or bbox[1] > shape.bbox[1]:
			bbox[1] = shape.bbox[1]
		if not bbox[2] or bbox[2] < shape.bbox[2]:
			bbox[2] = shape.bbox[2]
		if not bbox[3] or bbox[3] < shape.bbox[3]:
			bbox[3] = shape.bbox[3]

	print "found bbox to be %f,%f,%f,%f" % (bbox[0], bbox[1], bbox[2], bbox[3])

	#print tpl.substitute(width=options.width, height=options.width)


if __name__ == "__main__":
	main()

