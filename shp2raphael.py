#!/usr/bin/python
#
# shp2svg
#
# simple script to convert shapefile polygons to svg

from optparse import OptionParser
from string import Template
import sys, shapefile, json

def msg(str):
	sys.stderr.write(str + "\n");
	sys.stderr.flush()


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

	parser.add_option("-e", "--encoding", action="store", type="string", dest="encoding", default="latin-1",
		help="encoding of your attributes")

	parser.add_option("-p", "--precision", action="store", type="int", dest="precision", default="3",
		help="significant points after the decimal point")

	(options, args) = parser.parse_args()

	if not options.shpfile:
		parser.error('input-file is required')

	if not options.width and not options.height:
		parser.error('specify width, height or both')

	msg("opening shapefile")
	sf = shapefile.Reader(options.shpfile)

	if(options.listattrs):
		msg("listing attributes")
		fieldtypes = {"C": "Character", "N": "Number", "L": "Long", "D": "Date", "M": "Memo"}
		for field in sf.fields:
			if field[0] == "DeletionFlag":
				continue
			print "  %s (%s)" % (field[0], fieldtypes[field[1]])
		return

	shapes = sf.shapes()
	msg("working with %u shapes" % (len(shapes)))

	msg("scanning for bbox")
	bbox = [None, None, None, None]
	for shape in shapes:
		if not bbox[0] or bbox[0] > shape.bbox[0]:
			bbox[0] = shape.bbox[0]
		if not bbox[1] or bbox[1] > shape.bbox[1]:
			bbox[1] = shape.bbox[1]
		if not bbox[2] or bbox[2] < shape.bbox[2]:
			bbox[2] = shape.bbox[2]
		if not bbox[3] or bbox[3] < shape.bbox[3]:
			bbox[3] = shape.bbox[3]

	bboxsz = ( abs(bbox[0] - bbox[2]), abs(bbox[1] - bbox[3]) )
	msg("found bbox to be %f,%f,%f,%f (w=%u h=%u)" % (bbox[0], bbox[1], bbox[2], bbox[3], bboxsz[0], bboxsz[1]))

	aspect = float(bboxsz[0]) / float(bboxsz[1])
	if options.width:
		imgsz = (options.width, options.width / aspect)
	else:
		imgsz = (options.height * aspect, options.height)

	msg("calculated image-size as %u,%u" % (imgsz[0], imgsz[1]))

	attrs = [attr.strip() for attr in options.attrs.split(',')]
	attrids = {}
	idx = 0
	for field in sf.fields:
		if field[0] == "DeletionFlag":
			continue
		if field[0] in attrs:
			attrids[field[0]] = idx
		idx += 1

	jsonlist = []
	fmt = "%."+str(options.precision)+"f,%."+str(options.precision)+"f "
	for shapeidx, shape in enumerate(shapes):
		msg("accessing shape %u" % (shapeidx))
		jsonshp = {}
		jsonshp["paths"] = []
		for attr in attrs:
			msg("  copying attr %s" % (attr))
			jsonshp[attr] = sf.record(shapeidx)[attrids[attr]].decode(options.encoding, 'replace')

		msg("  shape.parts=" + str(shape.parts))
		msg("  shape.points.len=" + str(len(shape.points)))
		for partidx, start in enumerate(shape.parts):
			msg("  accessing shape-part %u" % (partidx))

			end = shape.parts[partidx+1]-1 if partidx < len(shape.parts)-1 else len(shape.points)-1
			msg("  copying points %u-%u" % (start, end))

			path = ""
			first = True
			for pointidx in range(start, end+1):
				point = shape.points[pointidx]
				if first:
					path += "M"
					first = False
				else:
					path += "L"
				
				pt = (
					           float(point[0] - bbox[0]) / float(bboxsz[0]) * float(imgsz[0]),
					imgsz[1] - float(point[1] - bbox[1]) / float(bboxsz[1]) * float(imgsz[1]),
				)
				path += fmt % pt

			jsonshp["paths"].append(path)

		jsonlist.append(jsonshp)


	msg("rendering template")
	f = open("template.html", 'r')
	tpl = Template(f.read())
	f.close()
	print tpl.substitute(width=imgsz[0], height=imgsz[1], json = json.dumps(jsonlist, indent=4, separators=(',', ': ')))


if __name__ == "__main__":
	main()

