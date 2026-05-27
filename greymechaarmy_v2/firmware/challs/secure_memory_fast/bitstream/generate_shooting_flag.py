FLAG = "grey{eh_dont_only_wayang}"
output = ""
for i in range(len(FLAG)):
    output += f"flag[{i}] = {ord(FLAG[i])};"
    if ((i+1) % 5 == 0):
        output += "\n"
    else:
        output += " "
print(len(FLAG))
print(output)