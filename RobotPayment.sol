// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract RobotPayment {
    struct Job {
        address user;
        string action;
        uint256 amount;
        uint256 timestamp;
        bool paid;
    }
    
    address public owner;
    Job[] public jobs;
    
    event JobCreated(uint256 jobId, address user, string action, uint256 amount);
    event PaymentReceived(uint256 jobId, address user, uint256 amount);
    
    constructor() {
        owner = msg.sender;
    }
    
    function createJob(string memory _action) public payable returns (uint256) {
        require(msg.value > 0, "Payment required");
        
        uint256 jobId = jobs.length;
        jobs.push(Job({
            user: msg.sender,
            action: _action,
            amount: msg.value,
            timestamp: block.timestamp,
            paid: true
        }));
        
        emit JobCreated(jobId, msg.sender, _action, msg.value);
        emit PaymentReceived(jobId, msg.sender, msg.value);
        
        return jobId;
    }
    
    function withdraw() public {
        require(msg.sender == owner, "Only owner can withdraw");
        payable(owner).transfer(address(this).balance);
    }
    
    function getJobCount() public view returns (uint256) {
        return jobs.length;
    }
    
    function getJob(uint256 _jobId) public view returns (
        address user,
        string memory action,
        uint256 amount,
        uint256 timestamp,
        bool paid
    ) {
        require(_jobId < jobs.length, "Job does not exist");
        Job storage job = jobs[_jobId];
        return (job.user, job.action, job.amount, job.timestamp, job.paid);
    }
}