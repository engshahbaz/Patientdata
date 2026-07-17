import time
import ctypes

# 1. Simulating Memory Regions (MR) using ctypes
# In real RDMA, these would be pinned physical memory addresses registered with the NIC hardware.
class MemoryRegion:
    def __init__(self, size: int, name: str):
        self.name = name
        self.size = size
        # Allocate a raw byte buffer in memory
        self.buffer = (ctypes.c_char * size)()
        self.address = ctypes.addressof(self.buffer)
    
    def write_data(self, data: bytes):
        self.buffer.value = data[:self.size]
        
    def read_data(self) -> bytes:
        return self.buffer.value

# 2. The RDMA Network Interface Card (vNIC) Simulation
class VirtualRDMANic:
    def __init__(self, name: str):
        self.name = name
        self.registered_regions = {}

    def register_memory(self, mr: MemoryRegion):
        """Hardware registers the physical memory address bounds."""
        self.registered_regions[mr.address] = mr
        print(f"[{self.name}] Registered Memory Region '{mr.name}' at structural address: {hex(mr.address)}")

    def rdma_write(self, remote_nic: 'VirtualRDMANic', remote_address: int, data: bytes):
        """
        ONE-SIDED OPERATION: The sender drives the transfer.
        The remote CPU is completely unaware and uninvolved during the transfer.
        """
        print(f"\n⚡ [RDMA] Initiating One-Sided RDMA Write from {self.name}...")
        time.sleep(0.2) # Simulate wire latency
        
        # Hardware directly accesses the remote memory address bypassing the OS
        if remote_address in remote_nic.registered_regions:
            target_mr = remote_nic.registered_regions[remote_address]
            
            # Direct Memory Copy (Hardware to Memory)
            target_mr.write_data(data)
            print(f"⚡ [RDMA] Success: Data injected directly into target address {hex(remote_address)}")
        else:
            raise MemoryError("RDMA Protection Fault: Remote address not registered or local keys invalid.")

# 3. Execution Simulation
if __name__ == "__main__":
    print("=== RDMA CORE CONCEPT SIMULATION ===")
    
    # Setup our virtual hardware nodes
    server_nic = VirtualRDMANic("Server_NIC")
    client_nic = VirtualRDMANic("Client_NIC")
    
    # Step 1: The Server sets up a buffer to receive data.
    # In RDMA, the receiver must 'pin' and register this memory beforehand.
    server_buffer = MemoryRegion(size=1024, name="Server_App_Receive_Buffer")
    server_nic.register_memory(server_buffer)
    
    # Step 2: The Server shares its memory address with the client.
    # (In the real world, this metadata exchange happens once via a standard TCP handshake).
    shared_remote_address = server_buffer.address
    print(f"[Handshake] Server sent its Target Memory Address to Client: {hex(shared_remote_address)}")
    
    # Step 3: Client wants to send data
    payload = b"Hello, this data went straight to your RAM without asking your CPU!"
    
    # Step 4: Perform the RDMA Write
    # Notice that we do not call a "receive()" function on the server side. 
    # The server CPU is doing nothing.
    client_nic.rdma_write(
        remote_nic=server_nic, 
        remote_address=shared_remote_address, 
        data=payload
    )
    
    # Step 5: Verify the server memory now holds the data
    print("\n=== Verification ===")
    print(f"Server CPU reads its memory buffer: '{server_buffer.read_data().decode()}'")