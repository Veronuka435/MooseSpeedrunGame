const config = {
  type: Phaser.AUTO,
  width: 800,
  height: 600,
  parent: 'phaser-example',
  physics: {
    default: 'arcade',
    arcade: { gravity: { y: 300 } }
  },
  scene: {
    preload: function () {
      this.load.image('moose', 'moose.png');
      this.load.image('platform', 'my_platform.png');
    },
    create: function () {
      this.add.image(400, 300, 'background.png');
      this.platform = this.physics.add.staticGroup();
      this.platform.create(400, 568, 'platform').setScale(1).refreshBody();
      this.player = this.physics.add.sprite(400, 500, 'moose');
      this.player.setBounce(0.2);
      this.player.setCollideWorldBounds(true);
      this.physics.add.collider(this.player, this.platform);
    },
    update: function () {
      let cursors = this.input.keyboard.createCursorKeys();
      if (cursors.left.isDown) {
        this.player.setVelocityX(-160);
      } else if (cursors.right.isDown) {
        this.player.setVelocityX(160);
      } else {
        this.player.setVelocityX(0);
      }
      if (cursors.up.isDown && this.player.body.touching.down) {
        this.player.setVelocityY(-330);
      }
    }
  }
};
const game = new Phaser.Game(config);