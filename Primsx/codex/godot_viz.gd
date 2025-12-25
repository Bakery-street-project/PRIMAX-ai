extends Node3D
func _ready():
    var file = File.new()
    file.open("res://trace.json", File.READ)
    var json = JSON.parse(file.get_as_text())
    var trace = json.result
    var line = ImmediateGeometry.new()
    add_child(line)
    line.begin(Mesh.PRIMITIVE_LINE_STRIP)
    for i in range(trace.x.size()):
        line.add_vertex(Vector3(trace.x[i], trace.y[i], trace.z[i]))
    line.end()
