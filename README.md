**# hEspresso**  
   
 DFT study of hydrogen adsorption on Mg2Ni surfaces with Nb2O5 and Fe catalysts using Quantum ESPRESSO.  
   
 **Project**  
- **System:** Mg2Ni(0001) slab (2x2x1, 72 atoms) with 12 A vacuum  
- **Goal:** Compare H2 adsorption energies with/without Nb2O5 and Fe nanoparticle catalysts  
- **Method:** Spin-polarized PBE, PAW/USPP pseudopotentials, dipole correction  
 **Structure**  
   
 mgh2-slab/          # Slab calculations  
   
  ├── main-write.ipynb    # Structure generation (ASE -> .pwi)  
   
  ├── *.pwi               # QE input files  
   
  ├── adsorption.py       # Adsorption energy analysis  
   
  ├── run.sh / eq_run.sh  # Run scripts  
   
  └── energy.sh           # Energy extraction  
   
    
 **Usage**  
   
 cd mgh2-slab  
   
  ./eq_run.sh nb2o5_cluster.pwi   # 1. Optimize Nb2O5 cluster  
   
  ./run.sh                         # 2. Run all slab calculations  
   
  ./energy.sh                      # 3. Extract energies  
   
  python adsorption.py             # 4. Compute adsorption energies  
   
    
