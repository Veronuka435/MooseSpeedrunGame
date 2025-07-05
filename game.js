const config = {
  type: Phaser.AUTO,
  width: 800,
  height: 600,
  parent: 'phaser-example',
  physics: {
    default: 'arcade',
    arcade: {
      gravity: { y: 500 },
      debug: false
    }
  },
  scene: {
    preload,
    create,
    update
  }
};

let player;
let cursors;
let platforms;

const game = new Phaser.Game(config);

function preload() {
  // Завантаження зображень
  this.load.image('background', 'background.png');
  this.load.image('platform', 'my_platform.png');
  this.load.image('moose', 'moose.png');
}

function create() {
  // Фон
  this.add.image(400, 300, 'background');

  // Платформи (група)
  platforms = this.physics.add.staticGroup();
  platforms.create(400, 568, 'platform').setScale(1).refreshBody();

  // Гравець
  player = this.physics.add.sprite(100, 450, 'moose');
  player.setBounce(0.2);
  player.setCollideWorldBounds(true);

  // Клавіші
  cursors = this.input.keyboard.createCursorKeys();

  // Колізія з платформами
  this.physics.add.collider(player, platforms);
}

function update() {
  // Рух вліво/вправо
  if (cursors.left.isDown) {
    player.setVelocityX(-160);
  } else if (cursors.right.isDown) {
    player.setVelocityX(160);
  } else {
    player.setVelocityX(0);
  }

  // Стрибок
  if (cursors.up.isDown && player.body.touching.down) {
    player.setVelocityY(-350);
  }
}
