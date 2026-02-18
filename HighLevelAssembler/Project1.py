import sys   #import sys to accept arguments in the command line (implemented later below)

#Registers and their corresponding values. Dictionary corresponds each register to its value according to the MIPS card.
REGISTERS = {
    '$zero':0, '$at':1,'$v0':2, '$v1':3,
    '$a0':4, '$a1':5, '$a2':6, '$a3':7,
    '$t0':8, '$t1':9, '$t2':10, '$t3':11, '$t4':12, '$t5':13, '$t6':14, '$t7':15,
    '$s0':16, '$s1':17, '$s2':18, '$s3':19, '$s4':20, '$s5':21, '$s6':22, '$s7':23,
    '$t8':24, '$t9':25,
    '$k0':26, '$k1':27, '$gp':28, '$sp':29, '$fp':30, '$s8':30, '$ra':31
}

#RTypeInstruction stores the function code in binary for the RTypeInstructions that don't use shift amounts and use rd, rs, and rt.
RTypeInstruction = {
    'add':  {'funct':'100000'},
    'addu': {'funct':'100001'},
    'sub':  {'funct':'100010'},
    'subu': {'funct':'100011'},
    'and':  {'funct':'100100'},
    'or':   {'funct':'100101'},
    'nor':  {'funct':'100111'},
    'slt':  {'funct':'101010'},
    'sltu': {'funct':'101011'}
}

#Different from RTypeInstruction because they set rs to 0 and use the shamt. Made a different function down below
RTypeInstructionWithShift = {
    'sll':  {'funct':'000000'},
    'srl':  {'funct':'000010'}
}

#Different from RtypeInstruction because rt, rd, and shamt need to be set to 0.
JrInstruction = {
    'jr':   {'funct':'001000'}
}

#All I type Instructions and their corresponding opcode are stored here.
ITypeInstruction = {
    'addi':  {'opcode':'001000'},
    'addiu': {'opcode':'001001'},
    'andi':  {'opcode':'001100'},
    'ori':   {'opcode':'001101'},
    'lui':   {'opcode':'001111'},
    'slti':  {'opcode':'001010'},
    'sltiu': {'opcode':'001011'},
    'lw':    {'opcode':'100011'},
    'sw':    {'opcode':'101011'},
    'lb':    {'opcode':'100000'},
    'lbu':   {'opcode':'100100'},
    'lhu':   {'opcode':'100101'},
    'sh':    {'opcode':'101001'},
    'sb':    {'opcode':'101000'},
    'beq':   {'opcode':'000100'},
    'bne':   {'opcode':'000101'}
}

#Used to convert the decimal of the registers (seen above in the registers dictionary) to their corresponding binary value.
def DecimalToBinary5bits(x):
    binary = ""
    while x > 0:
        binary = str(x % 2) + binary
        x //= 2
    length = 5 - len(binary)
    return "0"*length + binary

#Converts negative values too
#used to convert 16 bit immediate values into their binary values.
def DecimalToBinary16bits(x):
    if x < 0:
        x = (1 << 16) + x
    binary = bin(x)[2:]
    return binary.zfill(16)

#Read the function for the regular RTypeInstruction. It checks the rs, rd, and rt registers from the register dictionary and places them in the binary instruction
def readFunctionRcode(instructions, index, rawInstructions):
    try:
        #rd, rs, rt
        #op, rs, rt, rd, shamt, func
        rs = str(DecimalToBinary5bits(REGISTERS[instructions[2]]))
        rd = str(DecimalToBinary5bits(REGISTERS[instructions[1]]))
        rt = str(DecimalToBinary5bits(REGISTERS[instructions[3]]))
        function = str(RTypeInstruction[instructions[0]]["funct"])
        #print(RTypeInstruction[instructions[0]]["opcode"])
        return "000000" + rs + rt + rd + "00000" + function
    except:
       print("Cannot assemble " + rawInstructions + " at line " + str(index))  #If for whatever reason there is an error, it will print this error statement.
       return "Error"

#Read the instruction for the Itypeinstruction and send out a 32 bit binary instruction
def readFunctionIcode(instructions, index, rawInstructions):
    try:
        opcode = ITypeInstruction[instructions[0]]["opcode"]  #Find the opcode
        if instructions[0] == "beq" or instructions[0] == "bne": #If it is branching, the format is going to be different.
            # beq $rs, $rt, immediate
            rs = DecimalToBinary5bits(REGISTERS[instructions[1]])
            rt = DecimalToBinary5bits(REGISTERS[instructions[2]])
            imm = DecimalToBinary16bits(int(instructions[3])) 
            return opcode + rs + rt + imm
        elif instructions[0] == "lui": #If it is lui, the format is going to be different
            rt = DecimalToBinary5bits(REGISTERS[instructions[1]])
            rs = "00000"
            imm = DecimalToBinary16bits(int(instructions[2]))
            return opcode + rs + rt + imm
        elif len(instructions) == 3: #If it is an instruction like lw, the format is going to be different
            rt = DecimalToBinary5bits(REGISTERS[instructions[1]])
            offset_part = instructions[2]
            offset = offset_part[:offset_part.find('(')] #Find the offset from imm(rs)
            #print(offset)
            rs_value = offset_part[offset_part.find('(') + 1 : offset_part.find(')')] #Find the rs value from imm(rs)
            if offset == '': #If there's no imm value and it is just rs
                offset = '0'
            rs = DecimalToBinary5bits(REGISTERS[rs_value]) 
            imm = DecimalToBinary16bits(int(offset))
            return opcode + rs + rt + imm
        elif len(instructions) == 4: #If the instruction is something like addi, the format is going to be different
            rt = DecimalToBinary5bits(REGISTERS[instructions[1]])
            rs = DecimalToBinary5bits(REGISTERS[instructions[2]])
            imm = DecimalToBinary16bits(int(instructions[3]))
            return opcode + rs + rt + imm
    except:
       print("Cannot assemble " + rawInstructions + " at line " + str(index)) #If for whatever reason, an error is reached, print this out and end the code.
       return "Error"
    
#specific formatting used for the JR instruction    
def readFunctionJRcode(instructions, index, rawInstructions):
    try:
        rs = str(DecimalToBinary5bits(REGISTERS[instructions[1]]))
        rd = "00000"
        rt = "00000"
        shamt = "00000"
        function = str(JrInstruction[instructions[0]]["funct"])
        return "000000" + rs + rt + rd + shamt + function
    except:
        print("Cannot assemble " + rawInstructions + " at line " + str(index)) #If for whatever reason, an error is reached, print this out and end the code.
        return "Error"

#specific formatting used for instructions with the shift and dealing with the shamt portion of the r code instructions
def readFunctionRcodeWithShift(instructions, index, rawInstructions):
    try:
        #rd, rt, sh
        #op, rs, rt, rd, shamt, func
        rs = "00000"
        rt = str(DecimalToBinary5bits(REGISTERS[instructions[2]]))
        rd = str(DecimalToBinary5bits(REGISTERS[instructions[1]]))
        shamt = str(DecimalToBinary5bits(int(instructions[3])))
        function = str(RTypeInstructionWithShift[instructions[0]]["funct"])
        return "000000" + rs + rt + rd + shamt + function
    except:
       print("Cannot assemble " + rawInstructions + " at line " + str(index)) #If for whatever reason, an error is reached, print this out and end the code.
       return "Error"

#converts the binary instructions that I created into hex because thats what the assignment wants
def binaryToHex(binary):  
    # convert binary to int
    #print(binary)
    #print("HI")
    binary = str(binary)
    num = int(binary, 2)  
    # convert int to hexadecimal
    hex_num = format(num, 'x')
    length = 8 - len(hex_num)
    return length*"0" + str(hex_num)

#main assemble function
def assemble(filename):
    labels = {} #stores label locations
    output = [] #stores the output to later write it to the obj file
    with open(filename, "r") as file:  #goes through the file and finds out where each label is and the line is currently aat
        lineNumber = 0 #the line number to track where each label is
        for line in file:
            strippedline = line.strip()
            if(strippedline.endswith(":")): #if the line ends with a ":" it assumes it is a label
                label = strippedline[:-1] #takes the label name
                labels[label] = lineNumber #assigns the label name a line number and adds it to the dictionary "labels"
            else:
                lineNumber+=1 #only increments the line number when it doesn't go through a line with a label
    #print(labels)
    with open(filename, "r") as file: #Goes through a second time to actually convert all of the assembly instructions to machine codes
        i = 0 #index counter for offsets
        actualLine = 1 #actual line counter for error messages
        for line in file:
            strippedline = line.strip()
            nocommasline = strippedline.replace(',', '')
            words = nocommasline.split()  #strip the assembly to get an array of individual values including the function and the register values/shamt/offset (depending on function)
            if(":" in strippedline): #if it is a label, increment the actualLine count and then move on. don't bother with the rest of the code for this pass
                actualLine+=1
                continue
            #print(words)
            if(words[0] in RTypeInstruction): #if rTypeInstruction as specified above (no shamt and no jr)
                result = readFunctionRcode(words, actualLine, strippedline)
            elif(words[0] in RTypeInstructionWithShift): #if RTypeInstruction with a shift
                result = readFunctionRcodeWithShift(words, actualLine, strippedline)
            elif(words[0] in JrInstruction): #if function includes Jr
                result = readFunctionJRcode(words, actualLine, strippedline)
            elif(words[0] in ITypeInstruction):#if a ItypeInstruction
                if(words[0] == "beq" or words[0] == "bne"): #if its a branch function, need to set the offset if its a label and not a  numebr
                    labeler = words[3] #takes the label
                    if not labeler.isdigit(): #if its not a digit
                        if labeler not in labels: #if its an unkown label throw an error
                            print("Cannot assemble " + strippedline + " at line " + str(actualLine))
                            return
                    offset = labels[labeler] - (i+1) #calculate the offset of the current instruction vs the label its looking to branch to
                    words[3] = str(offset) #set the offset to be that value instead of the label
                result = readFunctionIcode(words, actualLine, strippedline) #run the ItypeInstruction method above
            else:
                print("Cannot assemble " + strippedline + " at line " + str(actualLine)) #throw an error if unrecognized
                return
            i+=1 #increment both indexes for offsets and actuallines
            actualLine+=1
            if(result == "Error"): #if you  ever got an error on any of the previous functions stop the function and don't generate a .obj file
                return
            output.append(binaryToHex(result)) #append the result to the output array
    outputFile = filename.split(".")[0] + ".obj"
    with open(outputFile, "w") as f: #read through the output array and write the lines to the .obj  file
        for line in output:
            f.write(line + "\n")
    
#R - Instruction : opcode, rs, rd, rt, shamt, function
#I - Instruction: opcode, rs, rt, immediate
for i in range(1,len(sys.argv)): #read through each argument that is given in the cli and pass it into the assemble function. If not found, throw a fileNotFound Error
    filename = sys.argv[i]
    try:
        assemble(filename)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found in the current directory.")

#print(DecimalToBinary16bits(-65))