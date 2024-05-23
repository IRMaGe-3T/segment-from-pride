#******************************************************************************
# FILENAME      : .perl script to launch for wrap-up
#******************************************************************************

#******************************************************************************
# EXTERNAL DECLARATIONS
#******************************************************************************
#
# perl template to handle file generation from PRIDE Research

use strict; # all perl scripts here in MR must use this.....
use Win32::Process;
use English;
use Getopt::Long;


{
    open (LOGFILE, '>>G:\\patch\\pride\\InlineExportXML\\perllog.txt');
    print "Starting your In-line PRIDE tool\n";
    my $roid = $ARGV[0];
    print "output series $roid";
    
    # Operator console directories
    
    my $dirXmlRecIn = "G:\\patch\\pride\\tempinputseries\\";
	# my $dirXmlRecIn = "C:\\TempinputSeries";
	
    my $dirXmlRecPost = "G:\\patch\\pride\\postprocessing\\";
	# my $dirXmlRecPost = "C:\\postprocessing\\";
	
    my $dirXmlRecOut = "G:\\patch\\pride\\tempoutputseries\\";
	# my $dirXmlRecOut = "C:\\TempoutputSeries\\";
	
    my $dirExe = "\"C:\\Program Files (x86)\\PMS\\Mipnet91x64\"";
    my $leacherExe = "$dirExe\\pridexmlleacher_win_cs.exe";
    
    
    
    # Cleanup the input/output directories
    
    my $command = "del /Q $dirXmlRecIn\\*.*";
    print ">>> $command\n" ;
    system($command);
    
    $command = "del /Q $dirXmlRecOut\\*.*";
    print ">>> $command\n" ;
    system($command);

    
    # Extracting the Xml/Rec file from the database
    
    print "Extracting the XML/REC file from the database\n";
    $command = "$leacherExe $roid";
    print ">>> $command\n" ;
    system($command);

    
    # check, whether 2 files are in dirXmlRecIn directory
    opendir(DNA,"$dirXmlRecIn");
    my $count = () = grep ! /^\.{1,2}/, readdir DNA;
    closedir(DNA);
    if ($count != 2)
    {
	print "XML/REC file export failed! Try again or get help!\n";
	print "Press any Key to continue or p to abort...\n";
	my $waiter = <stdin>;
	chomp $waiter;
	if ($waiter eq "p")
	{
	    exit 0;
	}
    }
    print LOGFILE "We have extracted the requested xml/rec file\n"; 
    
    print LOGFILE scalar localtime(); 
    
    # Open a NotePad. PRIDE will only try and read dirXmlRecOut when this NotePad is closed
    $command = "notepad.exe";
    system($command);
	
    print LOGFILE "\n"; 
  
    print LOGFILE scalar localtime(); 

    
}

