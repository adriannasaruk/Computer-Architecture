"""CPU functionality."""


import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256 
        self.reg = [0] * 8
        self.pc = 0 
        self.address = 0
        self.sp = len(self.reg) - 1 
        self.running = True
        self.fl = [False] * 8

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, value, address):
        self.ram[address] = value


    def load(self, filename) :

        if len(filename) < 2:
            print("Error: Insufficient arguments. Add a file from example folder into run command as arg[1]")
            sys.exit(0)
        
        try:
            with open(filename) as f:
                for line in f:
                    line = line.strip()
                    temp = line.split()
        
                    if len(temp) == 0:
                        continue
        
                    if temp[0][0] == '#':
                        continue
        
                    try:
                        self.ram[self.address] = int(temp[0], 2)
        
                    except ValueError:
                        print(f"Invalid number: {temp[0]}")
                        sys.exit(1)
        
                    self.address += 1
        
        except FileNotFoundError:
            print(f"Couldn't open {sys.argv[1]}")
            sys.exit(2)
        
        if self.address == 0:
            print("Program was empty!")


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc

        elif op == "CMP":
            equal = self.fl[7]
            greater_than = self.fl[6]
            less_than = self.fl[5]
            if self.reg[reg_a] == self.reg[reg_b]:
                equal = True
                greater_than = False
                less_than = False
            elif self.reg[reg_a] > self.reg[reg_b]:
                equal = False
                greater_than = True
                less_than = False
            else:
                equal = False
                greater_than = False
                less_than = True

            self.fl[5:] = [less_than, greater_than, equal]
        else:
            raise Exception("Unsupported ALU operation")
        

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ldi(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b

    def prn(self, operand_a):
        print(operand_a)

    def run(self):
        """Run the CPU."""
        LDI = 0b10000010
        PRN = 0b01000111
        HLT = 0b00000001
        MUL = 0b10100010
        PUSH = 0b01000101
        POP = 0b01000110
        CALL = 0b01010000
        RET = 0b00010001
        ADD =  0b10100000
        CMP = 0b10100111
        JMP = 0b01010100
        JEQ = 0b01010101
        JNE = 0b01010110

        running = True
        while self.running:
            
            if self.ram[self.pc] == HLT:
                self.running = False
            
            if self.ram[self.pc] == LDI:
                num_to_load = self.ram[self.pc + 2]
                reg_index = self.ram[self.pc + 1]
                self.reg[reg_index] = num_to_load
                self.pc += 3
            
            if self.ram[self.pc] == PRN:
                reg_to_print = self.ram[self.pc + 1]
                print(self.reg[reg_to_print])
                self.pc += 2
            
            if self.ram[self.pc] == MUL:
                first_reg = self.ram[self.pc + 1]
                sec_reg = self.ram[self.pc + 2]
                first_factor = self.reg[first_reg]
                sec_factor = self.reg[sec_reg]
                product = first_factor * sec_factor
                print(product)
                self.pc += 3

            if self.ram[self.pc] == ADD:
                first_reg = self.ram[self.pc + 1]
                sec_reg = self.ram[self.pc + 2]
                self.alu('ADD', first_reg, sec_reg)
                self.pc += 3

            if self.ram[self.pc] == CMP:
                first_reg = self.ram[self.pc + 1]
                sec_reg = self.ram[self.pc + 2]
                self.alu('CMP', first_reg, sec_reg)
                self.pc += 3

            if self.ram[self.pc] == JMP:
                reg_to_jump = self.ram[self.pc + 1]
                addr_to_jump = self.reg[reg_to_jump]
                self.pc = addr_to_jump

            if self.ram[self.pc] == JEQ:
                reg_to_jump = self.ram[self.pc + 1]
                addr_to_jump = self.reg[reg_to_jump]
                if self.fl[7] is True:
                    self.pc = addr_to_jump
                else:
                    self.pc += 2

            if self.ram[self.pc] == JNE:
                reg_to_jump = self.ram[self.pc + 1]
                addr_to_jump = self.reg[reg_to_jump]
                if self.fl[7] is False:
                    self.pc = addr_to_jump
                else:
                    self.pc += 2

            if self.ram[self.pc] == PUSH:
                self.reg[7] -= 1
                reg_to_push = self.ram[self.pc + 1]
                num_to_push = self.reg[reg_to_push]
                SP = self.reg[7]
                self.ram[SP] = num_to_push
                self.pc += 2

            if self.ram[self.pc] == POP:
                SP = self.reg[7]
                num_to_pop = self.ram[SP]
                reg_to_pop = self.ram[self.pc + 1]
                self.reg[reg_to_pop] = num_to_pop
                self.reg[7] += 1 
                self.pc += 2

            if self.ram[self.pc] == CALL:
                self.reg[7] -= 1
                SP = self.reg[7]
                addr_next_instruction = self.pc + 2
                self.ram[SP] = addr_next_instruction
                reg_to_call = self.ram[self.pc + 1]
                addr_to_goto = self.reg[reg_to_call]
                self.pc = addr_to_goto

            if self.ram[self.pc] == RET:
                SP = self.reg[7]
                addr_to_pop = self.ram[SP]
                self.pc = addr_to_pop
                self.reg[7] += 1