#include <linux/module.h>     /* Needed by all modules */ 
#include <linux/kernel.h>     /* Needed for KERN_INFO */ 
#include <linux/init.h>       /* Needed for the macros */ 
  
//The license type -- this affects runtime behavior 
MODULE_LICENSE("GPL"); 
  
// Your name should be visible when you use modinfo 
MODULE_AUTHOR("Uttam Ghosh"); 
  
// This description will be printed when you use modinfo 
MODULE_DESCRIPTION("A simple Hello world LKM!"); 
  
// The version of the module 
MODULE_VERSION("1.0"); 
  
// Implement hello_star module here to print two strings 
// CSX281: Loading kernel module... and Hello World!! 
// in the kerner buffer 
static int hello_start(void) {
	printk(KERN_INFO "CSX281: Loading kernel module...\n");
	printk(KERN_INFO "and Hello World!!\n");
	return 0;
}


// Implement hello_end module here and print the string CSX281: Exiting kernel module... 
// in the kernel buffer   
static void hello_exit(void) {
	printk(KERN_INFO "CSX281: Exiting kernel module...\n");
}

  
module_init(hello_start); 
module_exit(hello_exit);
