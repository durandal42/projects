//
//  PEMasterViewController.h
//  Project Euler
//
//  Created by David Sloan on 7/28/14.
//  Copyright (c) 2014 ___FULLUSERNAME___. All rights reserved.
//

#import <UIKit/UIKit.h>

@class PEDetailViewController;

@interface PEMasterViewController : UITableViewController

@property (strong, nonatomic) PEDetailViewController *detailViewController;

@end
